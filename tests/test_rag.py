import asyncio
from app.services.rag.service import search_policy


queries = [
    (
        "Mon téléphone est arrivé cassé dès la réception.",
        False,
        False,
    ),
    (
        "Mon téléphone est arrivé cassé dès la réception.",
        True,
        False,
    ),
    (
        "Mon téléphone est cassé, je l'ai fait tomber hier.",
        False,
        False,
    ),
    (
        "Je n'ai pas de photo mais mon produit est endommagé.",
        False,
        False,
    ),
    (
        "J'ai reçu le mauvais modèle de produit.",
        False,
        False,
    ),
    (
        "Sidi va à l'école.",
        False,
        False,
    ),
    (
        "Je dors chez moi.",
        False,
        False,
    ),
]


async def main():

    for query, image_received, audio_received in queries:

        print("=" * 80)
        print("Requête :", query)
        print("Image :", image_received)
        print("Audio :", audio_received)

        result = await search_policy(
            query,
            image_received=image_received,
            audio_received=audio_received,
        )

        print(result)
        print()


asyncio.run(main())