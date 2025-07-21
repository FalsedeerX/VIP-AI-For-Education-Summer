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
}


detect_os() {
	# detect linxu distribution
	if [[ -f /etc/os-release ]]; then
		source /etc/os-release
		DISTRO=$ID
	else
		echo "[-] Unabled to detect OS. /etc/os-release file not found."
		exit 1
	fi

	# linux distribution check
	if [[ "$DISTRO" != "arch" && "$DISTRO" != "debian" && "$DISTRO" != "ubuntu" ]]; then
		echo "[-] Unsupported Linux Distribution: $DISTRO"
		echo "[-] This script only supports Arch Linux and Debian-based distributions."
		exit 1
	fi

	# return the distro
	echo "$DISTRO"
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
}


main() {
	show_banner

	# detect the host operating system
	local distro=$(detect_os)
	echo "[+] Detected supported Linux distribution: '$distro', installation proceeding......"

	# install the required dependencies
	install_dependencies $distro
	echo

	# configure postgresql after installation
	setup_postgresql()
	echo

	# configure valkey after installation
}


main
