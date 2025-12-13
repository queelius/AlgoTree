#!/bin/bash
# Demo script for file-like metadata in AlgoTree shell
# Run with: python -m AlgoTree.shell.shell

cat << 'EOF'
# ==============================================================================
# AlgoTree Shell: File-Like Metadata Demo
# ==============================================================================

# Create a documentation tree
mktree docs
cd /docs

# Create sections using echo to write content
mkdir introduction
cd introduction
echo Welcome to AlgoTree! > summary
echo This library provides powerful tree operations. >> summary
echo See the API documentation for details. >> summary

# View what we created
cat summary

# Create another section
cd ..
mkdir installation
cd installation
echo Install via pip: > instructions
echo >> instructions
echo   pip install algotree >> instructions
echo >> instructions
echo Or from source: >> instructions
echo   git clone https://github.com/user/algotree >> instructions

cat instructions

# Create API docs section
cd ..
mkdir api
cd api
echo # Node Class > reference
echo >> reference
echo The Node class is the core of AlgoTree. >> reference
echo It provides immutable tree operations. >> reference

# Add version info
echo v2.0.0 > version
echo 2024-01-15 > updated

# View the structure
cd /docs
tree

# Show all sections with their attributes
ls -la

# Navigate and view specific content
cd introduction
cat summary

cd ../api
cat version
cat reference

# Query nodes
cd /docs
find -a "lambda n: 'version' in n.attrs"

# ==============================================================================
# Demo Complete!
# ==============================================================================

EOF
