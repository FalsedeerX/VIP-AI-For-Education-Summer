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
	return 0
}


setup_postgresql() {
	local distro="$1"

	# manually initialize postgresql if on Arch Linux
	if [[ "$distro" == "arch" ]]; then
		if [[ ! -d /var/lib/postgres/data ]]; then
		echo "[+] Initializing PostgreSQL's base cluster......"
		sudo -iu postgres initdb -D /var/lib/postgres/data
		fi
	fi

	# enable the postgresql service on the system
	echo "[+] Starting and enabling postgreSQL daemon on system......"
	sudo systemctl enable --now postgresql
	return 0
}


get_valkey_config() {
	# start the valkey daemon
	sudo systemctl start valkey

	# query on the service default configuration
	local exec_info=$(sudo systemctl show -p ExecStart valkey)
	local exec_args=$(echo "$exec_info" | sed -n "s/^ExecStart=.*argv\[]=\([^;]*\) ;.*$/\1/p")
	for arg in $exec_args; do
		if [[ "$arg" == *.conf && -f "$arg" ]]; then
			echo "$arg"
			sudo systemctl stop valkey
			return 0
		fi
	done

	# check the configuration in the default locations
	local default_paths=(
        "/etc/valkey/valkey.conf"
        "/etc/redis/valkey.conf"
        "/usr/local/etc/valkey.conf"
    )
    for path in "${default_paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            sudo systemctl stop valkey
            return 0
        fi
    done

    # If not found, stop the service and signal failure
    sudo systemctl stop valkey
    echo "[-] Valkey configuration file not found."
    return 1
}


setup_valkey() {	
	local config="$1" 

	# modify the valkey to listen for key expiration
	echo

	# daemon reload
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
	#install_dependencies $distro
	#echo

	# configure postgresql after installation
	#setup_postgresql $distro
	#echo

	# configure valkey after installation
	config=$(get_valkey_config)
	echo "$config"

	# configure  
	#echo
}


main
