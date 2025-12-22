import os

def collect_project_context(output_file="project_full_context.txt"):
    target_folders = ['notebooks', 'src', 'docs', 'models']
    valid_extensions = {'.py', '.ipynb', '.md', '.txt', '.csv'} # Added .csv for column headers only
    

    ignore_files = {'project_full_context.txt', 'accepted_2007_to_2018Q4.csv', 'prosperLoanData.csv'}

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("=== PROJECT STRUCTURE ===\n")
        for root, dirs, files in os.walk("."):
            if any(ignore in root for ignore in ['.git', '__pycache__', 'venv', 'archive']):
                continue
            level = root.count(os.sep)
            indent = " " * 4 * level
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            for f in files:
                if f not in ignore_files:
                    outfile.write(f"{indent}    {f}\n")
        outfile.write("\n" + "="*50 + "\n\n")

        
        for root, dirs, files in os.walk("."):
          
            if any(ignore in root for ignore in ['.git', '__pycache__', 'venv', 'archive', 'data']):
                continue

            for file in files:
                if file in ignore_files:
                    continue
                
                ext = os.path.splitext(file)[1]
                if ext not in valid_extensions:
                    continue

                file_path = os.path.join(root, file)
                
                
                outfile.write(f"START OF FILE: {file_path}\n")
                outfile.write("-" * 30 + "\n")

                try:
                    
                    if ext == '.ipynb':
                        import json
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for cell in data['cells']:
                                if cell['cell_type'] == 'markdown':
                                    outfile.write("".join(cell['source']) + "\n\n")
                                elif cell['cell_type'] == 'code':
                                    outfile.write("```python\n")
                                    outfile.write("".join(cell['source']) + "\n")
                                    outfile.write("```\n\n")
                    
                    
                    elif ext == '.csv':
                        import pandas as pd
                        df = pd.read_csv(file_path, nrows=0)
                        outfile.write(f"Columns: {list(df.columns)}\n")

                    
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            outfile.write(f.read())
                            
                except Exception as e:
                    outfile.write(f"Error reading file: {e}")

                outfile.write(f"\nEND OF FILE: {file_path}\n")
                outfile.write("=" * 50 + "\n\n")

    print(f"✅ Context generated! Upload '{output_file}' to the AI.")

if __name__ == "__main__":
    collect_project_context()