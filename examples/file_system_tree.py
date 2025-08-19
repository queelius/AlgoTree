#!/usr/bin/env python3
"""
Example: Building and analyzing a file system tree structure.
"""

from AlgoTree import TreeBuilder, FluentNode, dotmatch, export_tree


def build_file_system():
    """Build a sample file system tree."""
    fs = (TreeBuilder()
        .root("/", type="directory", size=0)
        .child("home", type="directory", size=0)
            .child("user", type="directory", size=0)
                .child("documents", type="directory", size=0)
                    .child("report.pdf", type="file", size=1024000)
                    .sibling("notes.txt", type="file", size=2048)
                    .sibling("presentation.pptx", type="file", size=5120000)
                    .up()
                .sibling("downloads", type="directory", size=0)
                    .child("data.csv", type="file", size=204800)
                    .sibling("app.zip", type="file", size=10240000)
                    .up()
                .sibling("pictures", type="directory", size=0)
                    .child("vacation.jpg", type="file", size=3072000)
                    .sibling("family.png", type="file", size=2048000)
                    .up(2)
            .sibling("alice", type="directory", size=0)
                .child("projects", type="directory", size=0)
                    .child("code.py", type="file", size=10240)
                    .up(3)
        .sibling("etc", type="directory", size=0)
            .child("config.ini", type="file", size=1024)
            .sibling("hosts", type="file", size=256)
        .build())
    
    return fs


def calculate_directory_sizes(tree):
    """Calculate total size for each directory."""
    def calc_size(node):
        if node.payload.get("type") == "file":
            return node.payload.get("size", 0)
        
        total = 0
        for child in node.children:
            total += calc_size(child)
        
        # Update directory size
        node.payload["size"] = total
        return total
    
    calc_size(tree)
    return tree


def analyze_file_system(fs):
    """Analyze the file system tree."""
    print("File System Analysis")
    print("=" * 50)
    
    # Count files and directories
    files = dotmatch(fs, "**[type=file]")
    dirs = dotmatch(fs, "**[type=directory]")
    
    print(f"Total directories: {len(dirs)}")
    print(f"Total files: {len(files)}")
    
    # Find large files (> 1MB)
    large_files = [f for f in files if f.payload.get("size", 0) > 1024000]
    print(f"\nLarge files (>1MB): {len(large_files)}")
    for f in large_files:
        size_mb = f.payload["size"] / 1024000
        paths = dotmatch(fs, f"**.{f.name}", return_paths=True)
        print(f"  {paths[0]}: {size_mb:.2f} MB")
    
    # Calculate total size
    fs = calculate_directory_sizes(fs)
    total_size = fs.payload.get("size", 0)
    print(f"\nTotal size: {total_size / 1024000:.2f} MB")
    
    # Find largest directory
    largest_dir = max(dirs, key=lambda d: d.payload.get("size", 0))
    print(f"\nLargest directory: {largest_dir.name} ({largest_dir.payload['size'] / 1024000:.2f} MB)")
    
    # File type distribution
    print("\nFile types:")
    from collections import Counter
    extensions = [f.name.split('.')[-1] if '.' in f.name else 'no_ext' 
                  for f in files]
    for ext, count in Counter(extensions).most_common():
        print(f"  .{ext}: {count} files")


def export_examples(fs):
    """Show different export formats."""
    print("\n" + "=" * 50)
    print("Export Examples")
    print("=" * 50)
    
    # ASCII tree
    print("\nASCII Tree:")
    print(export_tree(fs, "ascii"))
    
    # Save to different formats
    print("\nExporting to files...")
    export_tree(fs, "json", indent=2)  # Just show it can be done
    export_tree(fs, "graphviz", 
                node_attr=lambda n: {
                    "shape": "folder" if n.payload.get("type") == "directory" else "note",
                    "style": "filled",
                    "fillcolor": "lightblue" if n.payload.get("type") == "directory" else "lightgreen"
                })
    
    print("Export formats available: JSON, GraphViz, Mermaid, XML, YAML, HTML")


if __name__ == "__main__":
    # Build the file system tree
    fs = build_file_system()
    
    # Analyze it
    analyze_file_system(fs)
    
    # Show export examples
    export_examples(fs)