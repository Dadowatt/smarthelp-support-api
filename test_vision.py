from app.services.vision.clip import analyze_image


image_path = "chaise_casse.jpg"

result = analyze_image(image_path)

print(result)