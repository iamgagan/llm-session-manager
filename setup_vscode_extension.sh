#!/bin/bash

# LLM Session Manager - VS Code Extension Setup Script
# This script sets up the VS Code extension for development or installation

set -e

echo "=================================================="
echo "  LLM Session Manager - VS Code Extension Setup  "
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Please run this script from the llm-session-manager root directory${NC}"
    exit 1
fi

# Check if vscode-extension directory exists
if [ ! -d "vscode-extension" ]; then
    echo -e "${RED}Error: vscode-extension directory not found${NC}"
    exit 1
fi

echo "Step 1: Checking prerequisites..."
echo "--------------------------------"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found:${NC} $(node --version)"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found:${NC} $(npm --version)"

# Check for VS Code
if ! command -v code &> /dev/null; then
    echo -e "${YELLOW}⚠️  'code' command not found in PATH${NC}"
    echo "   You may need to install VS Code command line tools"
    echo "   VS Code > Command Palette > 'Shell Command: Install code command in PATH'"
else
    echo -e "${GREEN}✅ VS Code CLI found${NC}"
fi

echo ""
echo "Step 2: Installing dependencies..."
echo "--------------------------------"

cd vscode-extension

# Install npm dependencies
echo "Installing npm packages..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo "Step 3: Choose installation type"
echo "--------------------------------"
echo "1) Development mode (launches Extension Development Host)"
echo "2) Build and install extension (.vsix)"
echo "3) Just compile (no installation)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting Development Mode..."
        echo "Press F5 in VS Code to launch Extension Development Host"
        npm run compile
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Compilation successful${NC}"
            echo ""
            echo "Next steps:"
            echo "1. Open vscode-extension folder in VS Code"
            echo "2. Press F5 to launch Extension Development Host"
            echo "3. Extension will be active in the new window"
        fi
        ;;
    2)
        echo ""
        echo "Building and installing extension..."

        # Compile
        echo "Compiling TypeScript..."
        npm run compile

        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Compilation failed${NC}"
            exit 1
        fi

        # Package
        echo "Packaging extension..."
        npm run package

        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Packaging failed${NC}"
            exit 1
        fi

        # Install
        if command -v code &> /dev/null; then
            echo "Installing extension..."

            # Find the .vsix file
            VSIX_FILE=$(ls -t *.vsix 2>/dev/null | head -1)

            if [ -z "$VSIX_FILE" ]; then
                echo -e "${RED}❌ No .vsix file found${NC}"
                exit 1
            fi

            code --install-extension "$VSIX_FILE"

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Extension installed successfully${NC}"
                echo ""
                echo "Next steps:"
                echo "1. Reload VS Code"
                echo "2. Look for 'LLM Sessions' icon in the activity bar"
                echo "3. Configure settings: Preferences > Settings > LLM Session Manager"
            else
                echo -e "${RED}❌ Installation failed${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}⚠️  VS Code CLI not available${NC}"
            echo "Extension packaged successfully: $(ls -t *.vsix | head -1)"
            echo "Install manually: code --install-extension <file>.vsix"
        fi
        ;;
    3)
        echo ""
        echo "Compiling extension..."
        npm run compile

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Compilation successful${NC}"
            echo "Files compiled to: dist/"
        else
            echo -e "${RED}❌ Compilation failed${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "  Setup Complete!                                "
echo "=================================================="
echo ""
echo "Documentation:"
echo "  • Extension Guide: ../docs/VSCODE_EXTENSION_GUIDE.md"
echo "  • Skills Guide: ../docs/CLAUDE_CODE_SKILLS_GUIDE.md"
echo "  • Quick Setup: ../SKILLS_AND_VSCODE_SETUP.md"
echo ""
echo "Useful commands:"
echo "  • npm run compile    - Compile TypeScript"
echo "  • npm run watch      - Watch mode for development"
echo "  • npm run package    - Build .vsix file"
echo "  • npm run lint       - Run linter"
echo ""

cd ..
