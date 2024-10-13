def get_unique_categories(df):
    categories = set()
    for index, row in df.iterrows():
        # Collect 'Categoria Primaria' and 'Categoría Padre'
        primary_category = str(row['Categoria Primaria']).strip()
        parent_category = str(row['Categoría Padre']).strip()
        if primary_category:
            categories.add(primary_category)
        if parent_category:
            categories.add(parent_category)
    return categories