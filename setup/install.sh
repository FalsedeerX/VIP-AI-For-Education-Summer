#!/usr/bin/env bash
set -e


show_banner() {
	echo "########################"
	echo "# Purdue GPT Installer #"
	echo "########################"
	echo 
	echo "⚠️  Disclaimer:"
	echo "This installer is provided \"as is\" without guarantees."
	echo "Setup and configuration may differ across linux distributions."
	echo
	echo "🔧 Compatibility:"
	echo "This script is originally tested and verified **only on Arch Linux**."
	echo "It is also designed to support **Debian-based distributions**, but package compatibility is not guaranteed."
	echo "======================================================================"
	echo
	return 0
}


detect_os() {
	# detect linxu distribution
	if [[ -f /etc/os-release ]]; then
		source /etc/os-release
		DISTRO=$ID
	else
		return 1
	fi

	# linux distribution check
	if [[ "$DISTRO" != "arch" && "$DISTRO" != "debian" && "$DISTRO" != "ubuntu" ]]; then
		echo "[-] Unsupported Linux Distribution: $DISTRO"
		echo "[-] This script only supports Arch Linux and Debian-based distributions."
		exit 1
	fi

	# return the distro
	echo "$DISTRO"
	return 0
}


get_package_name() {
	local cmd="$1"
	local distro="$2"

	case "$cmd" in
		python)
			[[ "$distro" == "arch" ]] && echo "python" || echo "python3"
			;;
		pip)
			[[ "$distro" == "arch" ]] && echo "python-pip" || echo "python3-pip"
			;;
		valkey-server)
			[[ "$distro" == "arch" ]] && echo "valkey" || echo "valkey-server"
			;;
		node)
			echo "nodejs"
			;;
		npm)
			echo "npm"
			;;
		psql)
			echo "postgresql"
			;;
		*)
			echo "$cmd"
			;;
	esac
	return 0
}


install_if_missing() {
	local cmd="$1"
	local distro="$2"
	local pkg="$(get_package_name "$cmd" "$distro")"

	if ! command -v "$cmd" > /dev/null 2>&1; then
		echo "[-] Dependency '$cmd' is not found, Installing package 'pkg'......"
		if [[ "$distro" == "arch" ]]; then
			sudo pacman -Sy --noconfirm "$pkg"
		else
			sudo apt-get install -y "$pkg"
		fi
	else
		echo "[+] Dependency '$cmd' is present on system. Skipping installation."
	fi
	return 0
}


install_dependencies() {
	local distro="$1"
	local dependencies=("python" "pip" "node" "npm" "psql" "valkey-server")

	# update package info
	echo -e "[+] Updating system's package manager......\n"
	if [[ "$distro" == "arch" ]]; then
		sudo pacman -Sy --noconfirm
	else
		sudo apt-get update -y
	fi
	echo

	# install required dependencies
	for dependency in "${dependencies[@]}"; do
		install_if_missing "$dependency" "$distro"
	done

	# manually install the venv package for debian
	if [[ ! "$distro" = "arch" ]]; then
		sudo apt-get install -y python3-venv
	fi

	return 0
}


setup_postgres_auth() {
    local hba_file
    hba_file=$(find /etc/postgresql/ -type f -path "*/main/pg_hba.conf" | head -n1)

    if [[ ! -f "$hba_file" ]]; then
        echo "[-] Could not locate pg_hba.conf"
        return 1
    fi

    echo "[+] Located pg_hba.conf at $hba_file"
    echo "[+] Replacing 'peer' authentication with 'md5'..."
    sudo sed -i 's/^\(local[[:space:]]\+all[[:space:]]\+all[[:space:]]\+\)peer/\1md5/' "$hba_file"
    sudo systemctl restart postgresql
}



setup_postgresql() {
	local distro="$1"

	# manually initialize postgresql if on Arch Linux
	if [[ "$distro" == "arch" ]]; then
		if ! sudo test -d /var/lib/postgres/data; then
		echo "[+] Initializing PostgreSQL's base cluster......"
		sudo -iu postgres initdb -D /var/lib/postgres/data
		fi
	fi

	# modify authentication mode on debian
	if [[ ! "$distro" = "arch" ]]; then
		setup_postgres_auth
	fi

	# enable the postgresql service on the system
	echo "[+] Starting and enabling postgreSQL daemon on system......"
	sudo systemctl enable --now postgresql
	return 0
}


create_postgres_role() {
	local db_user="$1"
	local db_pass="$2"

	echo "[+] Creating role $db_user......"
	sudo -iu postgres psql <<SQL
DO \$\$
BEGIN
	IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$db_user') THEN
		EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '$db_user', '$db_pass');
	END IF;
END;
\$\$;
SQL
	return 0
}


create_postgres_db() {
	local db_name="$1"
	local db_owner="$2"

	echo "[+] Creating database $db_name......"
  	if sudo -iu postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '$db_name'" | grep -q 1; then
    	echo "[-] Database '$db_name' already exists. Skipping re-creation."
		return 0
  	else
    	sudo -iu postgres psql -c "CREATE DATABASE \"$db_name\" OWNER \"$db_owner\";"
  	fi
	return 0
}


create_postgres_tables() {
	local db_user="$1"
	local db_pass="$2"
	local db_name="$3"

	echo "[+] Importing table definition from schema.psql......"
	if [[ ! -f schema.psql ]]; then
		echo "[-] Table definition isn't located in the expected directory: $(pwd)"
		return 1
	fi

	# import and setup the table definition
	PGPASSWORD="$db_pass" psql -U "$db_user" -d "$db_name" -f schema.psql
	echo "[+] Schema import complete."
	return 0
}


provision_postgresql() {
	echo "[+] Setting up PostgreSQL environment and importing structure... "
	read -rp "[+] Enter a name for database: " db_name
	read -rp "[+] Enter a name for database user: " db_user
	read -rsp "[+] Create a password for $db_user: " db_pass
	echo

	# create the user in the base cluster
	create_postgres_role "$db_user" "$db_pass" 

	# create database and assign user as owner
	create_postgres_db "$db_name" "$db_user"

	# import the table schema from dump
	create_postgres_tables "$db_user" "$db_pass" "$db_name"
}


setup_valkey() {
	local distro="$1"
	local config="$2" 
	local service_name=$([[ "$distro" == "arch" ]] && echo "valkey" || echo "valkey-server")
	local setting_key="notify-keyspace-events"
	local setting_value="Ex"

	# check if the configuration is already satisfied
	if sudo grep -Eq "^[[:space:]]*${setting_key}[[:space:]]${setting_value}[[:space:]]*$" "$config"; then
		echo "[+] Valkey configuration is already setup properly. Skipping expiration callback setup."
		echo "[+] Starting and enabling Valkey daemon on system......"
		sudo systemctl enable --now "$service_name"
		return 0
	else
		echo "[-] Valkey's configuration not satisfy, modification proceeding......"
	fi

	# replace the previous configuration or append the new setting at the end of file
	if sudo grep -Eq "^[[:space:]]*${setting_key}[[:space:]]+" "$config"; then
		echo "[-] Previous configuration of key $setting_key detected in file $config"
		sudo sed -iE "s|^[[:space:]]*${setting_key}[[:space:]]\+.*$|${setting_key} ${setting_value}|" "$config"
	else
		echo "[-] Appending key $setting_key 's configuration to file $config"
		echo "${setting_key} ${setting_value}" | sudo tee -a "$config" > /dev/null
	fi
	echo "[+] Valkey configuration completed."

	# daemon reload
	echo "[+] Starting and enabling Valkey daemon on system......"
	sudo systemctl enable "$service_name"
	sudo systemctl restart "$service_name"
	return 0
}


setup_backend() {
	local original_dir="$(pwd)"

	echo "[+] Auto setting up the backend dependencies......"
	cd ../backend || {
		echo "[-] Failed to change directory into the backend folder !"
		return 1
	}

	if [[ -d .venv ]]; then
		echo "[+] Virtual envrionment directory .venv detected, skipping dependencies installation."
		cd "$original_dir"
		return 0
	fi

	echo "[+] Creating and activating virtual environment......"
	python3 -m venv .venv
	source .venv/bin/activate

	echo "[+] Installing required dependencies......"
	pip3 install -r requirements.txt
	pip3 install -e DatabaseAgent
	pip3 install -e SessionManager
	pip3 install -e Service
	deactivate

	echo "[+] Backend setup completed."
	cd "$original_dir"
	return 0
}


setup_frontend() {
	local original_dir=$(pwd)

	echo "[+] Auto setting up the frontend dependencies......"
	cd ../my-frontend || {
		echo "[-] Failed to change directory into the frontend folder !"
		return 1
	}

	echo "[+] Installing required dependencies......"
	npm install

	echo
	echo "[+] Frontend setup completed."
	cd "$original_dir"
	return 0
}


main() {
	show_banner

	# detect the host operating system
	local distro=$(detect_os)
	if [[ $? -ne 0 ]]; then
		echo "[-] Unable to detect host's Linux distribution, installation aborting......"
		exit 1
	else
		echo "[+] Detected supported Linux distribution: '$distro', installation proceeding......"
	fi

	# install the required dependencies
	install_dependencies "$distro"
	echo

	# configure postgresql after installation
	setup_postgresql "$distro"
	echo

	# auto setup db, user, tables in postgres
	provision_postgresql
	echo

	# configure valkey after installation
	setup_valkey "$distro" "/etc/valkey/valkey.conf"
	echo

	# create user + database schema import
	echo "[+] Auto setting up the database schemas and table......"
	echo

	# dependencies donwload for backend
	echo "[+] Auto setting up backend's environment......"
	setup_backend
	echo

	# dependencies download for frontend
	echo "[+] Auto setting up frontend's envrionemnt......"
	setup_frontend
	echo

	return 0
}


main
