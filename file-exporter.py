import pandas as pd
import os

# Load your Excel file
file_path = './adam_smith_complete.xlsx'
excel_data = pd.ExcelFile(file_path)
df = excel_data.parse('adam_smith_complete')  # Replace 'sheet_name' with the actual sheet name if needed

# Create a directory to save the files if it doesn't exist
output_dir = 'path'
os.makedirs(output_dir, exist_ok=True)

# Iterate through each row and save the 'speech' column as a text file
for idx, row in df.iterrows():
    speech_content = row['speech']  # Replace with the correct column name if different
    speech_id = row['speech_id']    # Use 'speech_id' or any unique identifier for the filename
    
    # Define the file name and path
    file_name = f"speech_{speech_id}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    # Write content to a text file
    with open(file_path, 'w') as file:
        file.write(speech_content)
        print(f"Speech {speech_id} saved to {file_path}")

print("Export completed!")
