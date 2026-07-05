import psycopg2
from remedies import REMEDIES

def populate():
    # Connect to the PostgreSQL database
    try:
        conn = psycopg2.connect(
            dbname="ollama_chat",
            user="postgres",
            password="postgres123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        print("Connected to database successfully.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    # 1. Custom Farming Guides to insert
    guides = [
        {
            "content": (
                "Farming Guide: Mango Fruit Red Dots. Red dots or spots on mango fruits are commonly caused by Anthracnose "
                "(a fungal infection caused by Colletotrichum gloeosporioides) or bacterial black spot. Symptoms start as "
                "small, water-soaked, circular, or irregular lesions on leaves and fruit, which later turn brown, black, or red dots. "
                "Organic cure: Spray copper fungicide, liquid seaweed, or potassium bicarbonate. Prune branches to improve air "
                "circulation. Chemical cure: Apply chlorothalonil or mancozeb. Prevention: Apply neem oil before fruit set, rake and "
                "destroy fallen leaves."
            )
        },
        {
            "content": (
                "Farming Guide: How to Grow Perfect Bananas. Bananas are heavy feeders requiring warm weather, rich, well-draining soil, "
                "constant moisture, and shelter from wind. 1. Soil: Ideal pH is 5.5 - 6.5. Mix organic compost or manure heavily into the "
                "planting hole. 2. Watering: Water deeply and keep soil consistently moist but never soggy to prevent root rot. 3. Nutrients: "
                "High potassium fertilizers (NPK 8-10-8 or similar) are essential for healthy banana fruiting. 4. Pruning: Keep only one main "
                "fruiting stem and one sucker (follower) per plant to maximize yield."
            )
        },
        {
            "content": (
                "Farming Guide: Precautions Before Crop Raising. 1. Soil Testing: Always test the soil pH and nutrient levels beforehand "
                "to prepare target amendments. 2. Seed Selection: Choose certified, disease-resistant seeds/varieties. 3. Tillage: Till the "
                "field properly to control weeds, expose pests, and improve soil aeration. 4. Soil Treatment: Solarize the soil or mix in "
                "beneficial microbes like Trichoderma (a bio-fungicide) to prevent root rot and soil-borne wilt diseases. 5. Drainage: Set up "
                "proper drainage channels to avoid waterlogging."
            )
        }
    ]

    # Add remedies from remedies.py
    for key, data in REMEDIES.items():
        title = key.replace("___", " - ").replace("_", " ")
        summary = data.get("summary", "")
        organic = ", ".join(data.get("organic", []))
        chemical = ", ".join(data.get("chemical", []))
        prevention = ", ".join(data.get("prevention", []))

        content = f"KrishiSetu Verified Manual: For {title}, this is a disease with the following details. Summary: {summary} "
        if organic:
            content += f"Organic Treatments: {organic}. "
        if chemical:
            content += f"Chemical Treatments: {chemical}. "
        if prevention:
            content += f"Prevention: {prevention}."

        guides.append({"content": content})

    # Insert each unique guide/remedy
    inserted = 0
    for guide in guides:
        content = guide["content"]
        # Check if it already exists
        cursor.execute("SELECT id FROM knowledge_chunk WHERE content = %s", (content,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO knowledge_chunk (content, embedding) VALUES (%s, NULL)", (content,))
            inserted += 1

    conn.commit()
    print(f"Successfully checked all entries. Inserted {inserted} new farming knowledge chunks into 'knowledge_chunk' table.")
    
    # Trigger a re-indexing in Spring Boot if we added new chunks
    if inserted > 0:
        import requests
        try:
            r = requests.post("http://localhost:8090/api/knowledge/reindex", timeout=10)
            if r.status_code == 200:
                print("Triggered Spring Boot manual re-indexing successfully.")
            else:
                print(f"Could not trigger re-indexing automatically: {r.status_code}")
        except Exception as e:
            print(f"Could not connect to Spring Boot re-indexing API: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    populate()
