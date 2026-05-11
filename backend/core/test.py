from database import news_collection

test_data = {
    "title": "Test News"
}

news_collection.insert_one(test_data)

print("Data Inserted Successfully")