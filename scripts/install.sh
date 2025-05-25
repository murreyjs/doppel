#!/bin/bash
# Installation script for doppel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    if ! command_exists python3; then
        print_error "Python 3 is required but not installed."
        print_error "Please install Python 3.7 or later and try again."
        exit 1
    fi

    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_status "Found Python $python_version"

    # Check if Python version is >= 3.7
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
        print_error "Python 3.7 or later is required. Found Python $python_version"
        exit 1
    fi

    if ! command_exists pip3; then
        print_error "pip3 is required but not installed."
        print_error "Please install pip3 and try again."
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Install doppel
install_doppel() {
    print_status "Installing doppel..."

    # Check if we're in the doppel directory
    if [[ ! -f "setup.py" ]] || [[ ! -d "doppel" ]]; then
        print_error "This script must be run from the doppel project directory"
        print_error "Make sure you're in the directory containing setup.py"
        exit 1
    fi

    # Check if we're in a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_status "Virtual environment detected: $VIRTUAL_ENV"
        print_status "Installing doppel in development mode..."
        pip install -e .
    else
        print_status "No virtual environment detected"

        # Try pipx first (recommended for applications)
        if command_exists pipx; then
            print_status "Using pipx for installation..."
            pipx install -e .
        else
            print_warning "pipx not found. Trying pip with --user flag..."
            # Try with --user flag first
            if pip3 install -e . --user 2>/dev/null; then
                print_status "Installed with --user flag"
            else
                print_warning "Standard installation failed due to externally managed environment"
                print_warning "Trying with --break-system-packages flag..."
                pip3 install -e . --user --break-system-packages
            fi
        fi
    fi

    print_success "Doppel installed successfully!"
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."

    # Check if doppel command is available
    if command_exists doppel; then
        version=$(doppel --version 2>/dev/null | grep -o "doppel [0-9.]*" | cut -d' ' -f2)
        print_success "Doppel $version is installed and available"

        # Show installation path
        doppel_path=$(which doppel)
        print_status "Installed at: $doppel_path"
    else
        print_warning "Doppel command not found in PATH"
        print_warning "You may need to add ~/.local/bin to your PATH"
        print_warning "Add this line to your ~/.bashrc or ~/.zshrc:"
        print_warning "export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

# Install development dependencies
install_dev_deps() {
    if [[ "$1" == "--dev" ]]; then
        print_status "Installing development dependencies..."

        if [[ -n "$VIRTUAL_ENV" ]]; then
            pip install -e ".[dev]"
        elif command_exists pipx; then
            print_warning "pipx doesn't support dev dependencies well"
            print_warning "Consider using a virtual environment for development"
        else
            pip3 install -e ".[dev]" --user --break-system-packages 2>/dev/null || \
            pip3 install -e ".[dev]" --user
        fi

        print_success "Development dependencies installed"
    fi
}

# Show usage information
show_usage() {
    print_success "Installation complete!"
    echo
    print_status "Quick start:"
    echo "  doppel                    # Search current directory"
    echo "  doppel /path/to/folder    # Search specific directory"
    echo "  doppel --content ~/docs   # Compare file content"
    echo "  doppel --dry-run .        # Preview without deletion"
    echo
    print_status "For more information:"
    echo "  doppel --help"
    echo "  cat docs/usage.md"
    echo "  cat docs/examples.md"
}

# Main installation process
main() {
    echo "=========================================="
    echo "         Doppel Installation Script"
    echo "=========================================="
    echo

    check_prerequisites
    echo

    install_doppel
    echo

    install_dev_deps "$1"
    echo

    verify_installation
    echo

    show_usage
}

# Run with development flag if requested
if [[ "$1" == "--dev" ]]; then
    print_status "Development installation requested"
fi

main "$1"