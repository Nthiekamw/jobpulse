import os
from pyspark.sql import SparkSession, functions as F

spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("test_enrichissement_silver")
    .config("spark.driver.memory", "3g")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# Offres France Travail
brut = spark.read.json("data/bronze/export_jsonl/*.jsonl")
offres = brut.filter(
    "identifier.partner_label != 'recruteurs_lba' AND offer IS NOT NULL"
)

ft = offres.select(
    F.coalesce(F.col("identifier.partner_job_id"), F.col("identifier.id")).alias("id_offre"),
    F.col("identifier.partner_label").alias("source"),
    F.col("offer.title").alias("titre"),
    F.col("offer.description").alias("description"),
    F.col("offer.desired_skills").alias("competences_declarees"),
    F.col("offer.rome_codes").alias("codes_rome"),
    F.col("workplace.name").alias("entreprise"),
    F.col("workplace.size").alias("taille_entreprise"),
    F.col("workplace.location.address").alias("adresse"),
    F.col("contract.duration").alias("duree_mois"),
    F.col("contract.remote").alias("mode_travail"),
    F.col("contract.type").alias("types_contrat"),
    F.col("offer.publication.creation").alias("date_publication"),
    F.col("workplace.domain.naf.code").alias("code_naf"),
    F.col("workplace.domain.naf.label").alias("secteur_naf"),
    F.lit(None).cast("double").alias("salaire_min"),
    F.lit(None).cast("double").alias("salaire_max"),
    F.lit(None).cast("string").alias("categorie_source")
).dropDuplicates(["source", "id_offre"])

# Échantillon Adzuna déjà collecté
fichier = "data/bronze/adzuna/test_page1.json"

if os.path.exists(fichier):
    data = spark.read.option("multiLine", True).json(fichier)

    adzuna = data.select(F.explode("results").alias("o")).select(
        F.col("o.id").cast("string").alias("id_offre"),
        F.lit("adzuna").alias("source"),
        F.col("o.title").alias("titre"),
        F.col("o.description").alias("description"),
        F.array().cast("array<string>").alias("competences_declarees"),
        F.array().cast("array<string>").alias("codes_rome"),
        F.col("o.company.display_name").alias("entreprise"),
        F.lit(None).cast("string").alias("taille_entreprise"),
        F.col("o.location.display_name").alias("adresse"),
        F.lit(None).cast("long").alias("duree_mois"),
        F.col("o.contract_time").cast("string").alias("mode_travail"),
        F.when(
            F.col("o.contract_type").isNotNull(),
            F.array(F.col("o.contract_type").cast("string"))
        ).otherwise(F.array().cast("array<string>")).alias("types_contrat"),
        F.col("o.created").alias("date_publication"),
        F.lit(None).cast("string").alias("code_naf"),
        F.lit(None).cast("string").alias("secteur_naf"),
        F.col("o.salary_min").cast("double").alias("salaire_min"),
        F.col("o.salary_max").cast("double").alias("salaire_max"),
        F.col("o.category.label").alias("categorie_source")
    )

    ft = ft.unionByName(adzuna, allowMissingColumns=True)
    ft = ft.dropDuplicates(["source", "id_offre"])

ft = ft.withColumn(
    "code_postal", F.regexp_extract("adresse", r"\b(\d{5})\b", 1)
).withColumn(
    "departement", F.substring("code_postal", 1, 2)
)

destination = "data/silver/export_offres_enrichi_test"
ft.write.mode("overwrite").parquet(destination)

resultat = spark.read.parquet(destination)

print("\n========== TEST SILVER ENRICHI ==========")
print("Total offres :", resultat.count())
print("Colonnes :", len(resultat.columns))
resultat.printSchema()

print("\n========== TYPES DE CONTRAT ==========")
resultat.select(F.explode_outer("types_contrat").alias("type")) \
    .groupBy("type").count().orderBy(F.desc("count")).show(20, False)

print("\n========== SALAIRES ADZUNA ==========")
resultat.filter(
    (F.col("source") == "adzuna") & F.col("salaire_min").isNotNull()
).select("titre", "salaire_min", "salaire_max").show(15, False)

print("\n========== DATES ==========")
resultat.groupBy(
    F.substring("date_publication", 1, 7).alias("mois")
).count().orderBy("mois").show(30, False)

print("\n========== SECTEURS ==========")
resultat.filter(F.col("secteur_naf").isNotNull()) \
    .groupBy("secteur_naf").count() \
    .orderBy(F.desc("count")).show(15, False)

spark.stop()
