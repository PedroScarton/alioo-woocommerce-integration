def get_unique_categories(df):
    categories = set()
    for index, row in df.iterrows():
        row_categories = set()

        # Collect 'Categoria Primaria' and 'Categoría Padre'
        primary_category = str(row['Categoria Primaria']).strip()
        parent_category = str(row['Categoría Padre']).strip()

        split_primary_category = primary_category.split(',')
        split_parent_category = parent_category.split(',')

        # Save the split strings to a new
        row_categories.update(split_primary_category)
        row_categories.update(split_parent_category)

        # Remove duplicates and empty strings
        row_categories = set(filter(None, row_categories))

        # Remove nan strings from the set
        row_categories.discard('nan')

        # Add the row categories to the set of all categories
        categories.update(row_categories)

        # Add the row categories to the dataframe row itself
        df.at[index, 'categories'] = row_categories

    return categories