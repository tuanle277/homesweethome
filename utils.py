from setup import *

def input_report_to_sheet(report, place):
  filename = f"data/{place}.xlsx"
  # Check if the file exists
  if os.path.exists(filename):
      # File exists, so read it into a DataFrame
      existing_df = pd.read_excel(filename)
  else:
      # File does not exist, create an empty DataFrame
      # Assuming you know the column names ahead of time, or they can be inferred from the list of dictionaries
      existing_df = pd.DataFrame(report)

  # Convert the new data to a DataFrame
  new_df = pd.DataFrame(report)

  # Save the updated DataFrame back to the Excel file
  new_df.to_excel(filename, index=False)

  print(f"Excel file '{filename}' has been updated with new data.")
  print("Data parsed successfully.")
