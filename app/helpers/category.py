from app.models import Categories

def getCategoriesPair():
    categories = []
    query = Categories.objects()
    for category in query:
        categories.append((category.id, category.name))
        
    return categories