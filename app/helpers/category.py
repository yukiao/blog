from app.models import Category

def getCategoriesPair():
    categories = []
    query = Category.objects()
    for category in query:
        categories.append((category.id, category.name))
    return categories