import kagglehub

# Download latest version
path = kagglehub.dataset_download("wintersoldierv/1-lakh-companies-dataset")

print("Path to dataset files:", path)