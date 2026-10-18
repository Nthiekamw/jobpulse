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
    F.col("contract.remote").alias("mode_travail"),
).dropDuplicates(["source", "id_offre"])

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
print("Temps (secondes) :", round(time.time() - debut))
spark.stop()
