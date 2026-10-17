from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.master("local[2]").appName("silver_offres").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

brut = spark.read.option("multiLine", True).json("data/bronze/*/offres_*.json")
offres = brut.select(F.explode("jobs").alias("j")).select("j.*")

silver = offres.select(
    F.col("identifier.partner_job_id").alias("id_offre"),
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
)

silver = silver.dropDuplicates(["id_offre"])
silver = silver.withColumn("code_postal", F.regexp_extract("adresse", r"\b(\d{5})\b", 1))
silver = silver.withColumn("departement", F.substring("code_postal", 1, 2))
silver.write.mode("overwrite").parquet("data/silver/offres")

print("Offres avant dedoublonnage :", offres.count())
print("Offres apres dedoublonnage :", silver.count())
silver.select("source", "titre", "departement").show(5, truncate=40)
spark.stop()
