from app.services.rag.service import search_policy

queries = [
    "Mon téléphone est arrivé cassé avec l'écran fissuré.",
    "J'ai reçu le mauvais modèle de produit.",
    "Il manque une pièce dans le colis.",
    "Mon colis est arrivé avec 6 jours de retard.",
    "Le transporteur indique que mon colis est perdu depuis 8 jours.",
    "Le produit est tombé après la livraison et s'est cassé.",
    "Je n'ai pas de photo mais mon produit est endommagé.",
]

for query in queries:
    print("=" * 80)
    print("Requête :", query)
    print(search_policy(query))
    print()