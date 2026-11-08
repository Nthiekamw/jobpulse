import os
import time
from pyspark.sql import SparkSession, functions as F

debut = time.time()
spark = (SparkSession.builder.master("local[2]").appName("silver_export")
         .config("spark.driver.memory", "3g").getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

brut = spark.read.json("data/bronze/export_jsonl/*.jsonl")

offres = brut.filter("identifier.partner_label != 'recruteurs_lba' AND offer IS NOT NULL")
recruteurs = brut.filter("identifier.partner_label = 'recruteurs_lba'")
id_ = F.coalesce(F.col("identifier.partner_job_id"), F.col("identifier.id"))

silver = offres.select(
    id_.alias("id_offre"),
    F.col("identifier.partner_label").alias("source"),
    F.col("offer.title").alias("titre"),
    F.col("offer.description").alias("description"),
    F.col("offer.desired_skills").alias("competences_declarees"),
    F.col("offer.rome_codes").alias("codes_rome"),
    F.col("workplace.name").alias("entreprise"),
    F.col("workplace.size").alias("taille_entreprise"),
    F.col("workplace.location.address").alias("adresse"),
    F.col("contract.duration").alias("duree_mois"),
    F.col("contract.remote").cast("string").alias("mode_travail"),
    F.col("contract.type").alias("types_contrat"),
    F.col("offer.publication.creation").cast("string").alias("date_publication"),
    F.col("workplace.domain.naf.code").cast("string").alias("code_naf"),
    F.col("workplace.domain.naf.label").cast("string").alias("secteur_naf"),
    F.lit(None).cast("double").alias("salaire_min"),
    F.lit(None).cast("double").alias("salaire_max"),
    F.lit(None).cast("string").alias("categorie_source"),
    F.lit(None).cast("string").alias("salaire_estime"),
    F.lit(None).cast("string").alias("temps_travail"),
    F.when(
        F.array_contains(F.col("contract.type"), "Apprentissage") |
        F.array_contains(F.col("contract.type"), "Professionnalisation"),
        "Alternance"
    ).otherwise(None).alias("type_contrat_normalise")
).dropDuplicates(["source", "id_offre"])

fichier_adzuna = "data/bronze/" + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + "/adzuna_page_1.json"

if os.path.exists(fichier_adzuna):
    adzuna_brut = spark.read.option("multiLine", True).json(fichier_adzuna)
    adzuna = adzuna_brut.select(F.explode("results").alias("offre")).select(
        F.col("offre.id").cast("string").alias("id_offre"),
        F.lit("adzuna").alias("source"),
        F.col("offre.title").alias("titre"),
        F.col("offre.description").alias("description"),
        F.array().cast("array<string>").alias("competences_declarees"),
        F.array().cast("array<string>").alias("codes_rome"),
        F.col("offre.company.display_name").alias("entreprise"),
        F.lit(None).cast("string").alias("taille_entreprise"),
        F.col("offre.location.display_name").alias("adresse"),
        F.lit(None).cast("long").alias("duree_mois"),
        F.lit(None).cast("string").alias("mode_travail"),
        F.when(F.col("offre.contract_type").isNotNull(),
               F.array(F.col("offre.contract_type").cast("string"))
        ).otherwise(F.array().cast("array<string>")).alias("types_contrat"),
        F.col("offre.created").cast("string").alias("date_publication"),
        F.lit(None).cast("string").alias("code_naf"),
        F.lit(None).cast("string").alias("secteur_naf"),
        F.col("offre.salary_min").cast("double").alias("salaire_min"),
        F.col("offre.salary_max").cast("double").alias("salaire_max"),
        F.col("offre.category.label").cast("string").alias("categorie_source"),
        F.col("offre.salary_is_predicted").cast("string").alias("salaire_estime"),
        F.col("offre.contract_time").cast("string").alias("temps_travail"),
        F.when(F.col("offre.contract_type") == "permanent", "CDI")
         .when(F.col("offre.contract_type") == "contract", "Contrat temporaire à qualifier")
         .otherwise(None).alias("type_contrat_normalise")
    )
    silver = silver.unionByName(adzuna).dropDuplicates(["source", "id_offre"])
    print("Offres Adzuna integrees :", adzuna.count())
else:
    print("Fichier Adzuna absent : integration ignoree")


fichier_jooble = "data/bronze/" + __import__("datetime").datetime.now().strftime("%Y-%m-%d") + "/jooble_page_1.json"

if os.path.exists(fichier_jooble):
    jooble_brut = spark.read.option("multiLine", True).json(fichier_jooble)
    jooble = jooble_brut.select(F.explode("jobs").alias("offre")).select(
        F.col("offre.id").cast("string").alias("id_offre"),
        F.lit("jooble").alias("source"),
        F.col("offre.title").alias("titre"),
        F.col("offre.snippet").alias("description"),
        F.array().cast("array<string>").alias("competences_declarees"),
        F.array().cast("array<string>").alias("codes_rome"),
        F.col("offre.company").alias("entreprise"),
        F.lit(None).cast("string").alias("taille_entreprise"),
        F.col("offre.location").alias("adresse"),
        F.lit(None).cast("long").alias("duree_mois"),
        F.lit(None).cast("string").alias("mode_travail"),
        F.when(F.col("offre.type").isNotNull(),
               F.array(F.col("offre.type").cast("string"))
        ).otherwise(F.array().cast("array<string>")).alias("types_contrat"),
        F.col("offre.updated").cast("string").alias("date_publication"),
        F.lit(None).cast("string").alias("code_naf"),
        F.lit(None).cast("string").alias("secteur_naf"),
        F.lit(None).cast("double").alias("salaire_min"),
        F.lit(None).cast("double").alias("salaire_max"),
        F.lit("Jooble").alias("categorie_source"),
        F.lit(None).cast("string").alias("salaire_estime"),
        F.lit(None).cast("string").alias("temps_travail"),
        F.when(F.lower(F.col("offre.type")).contains("cdi"), "CDI")
         .when(F.lower(F.col("offre.type")).contains("cdd"), "CDD")
         .when(F.lower(F.col("offre.type")).contains("intérim") |
               F.lower(F.col("offre.type")).contains("interim"), "Intérim")
         .otherwise(None).alias("type_contrat_normalise")
    )
    silver = silver.unionByName(jooble).dropDuplicates(["source", "id_offre"])
    print("Offres Jooble integrees :", jooble.count())
else:
    print("Fichier Jooble absent : integration ignoree")

rec = recruteurs.select(
    F.col("identifier.id").alias("id_recruteur"),
    F.col("workplace.name").alias("entreprise"),
    F.col("workplace.siret").alias("siret"),
    F.col("workplace.size").alias("taille_entreprise"),
    F.col("workplace.location.address").alias("adresse"),
).dropDuplicates(["id_recruteur"])

def avec_dept(df):
    df = df.withColumn("code_postal", F.regexp_extract("adresse", r"\b(\d{5})\b", 1))
    return df.withColumn("departement", F.substring("code_postal", 1, 2))

avec_dept(silver).write.mode("overwrite").parquet("data/silver/export_offres")
avec_dept(rec).write.mode("overwrite").parquet("data/silver/export_recruteurs")

print("Offres :", spark.read.parquet("data/silver/export_offres").count())
print("Recruteurs :", spark.read.parquet("data/silver/export_recruteurs").count())
print("Colonnes :", len(spark.read.parquet("data/silver/export_offres").columns))
print("Temps (secondes) :", round(time.time() - debut))
spark.stop()
