from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.master("local[2]").appName("gold").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

s = spark.read.parquet("data/silver/export_offres_competences")
total = s.count()

top = s.select(F.explode("competences_extraites").alias("technologie"))
top = top.groupBy("technologie").count().withColumnRenamed("count", "nb_offres")
top = top.withColumn("pct_offres", F.round(F.col("nb_offres") * 100 / total, 1))
top = top.orderBy(F.desc("nb_offres"))

dept = s.filter("departement != ''").groupBy("departement").count()
dept = dept.withColumnRenamed("count", "nb_offres").orderBy(F.desc("nb_offres"))

source = s.groupBy("source").count().withColumnRenamed("count", "nb_offres")
source = source.orderBy(F.desc("nb_offres"))

rome = s.select(F.explode("codes_rome").alias("code_rome")).groupBy("code_rome").count()
rome = rome.withColumnRenamed("count", "nb_offres").orderBy(F.desc("nb_offres"))

contrats = (
    s.withColumn(
        "type_contrat_normalise",
        F.coalesce(F.col("type_contrat_normalise"), F.lit("Non renseigné"))
    )
    .groupBy("type_contrat_normalise")
    .count()
    .withColumnRenamed("type_contrat_normalise", "contrat")
    .withColumnRenamed("count", "nb_offres")
    .orderBy(F.desc("nb_offres"))
)

tables = [("offres_par_contrat", contrats),
          ("top_technologies", top), ("offres_par_departement", dept),
          ("offres_par_source", source), ("offres_par_rome", rome)]
for nom, df in tables:
    df.coalesce(1).write.mode("overwrite").parquet("data/gold_export/" + nom)
    print(nom, ":", df.count(), "lignes")

top.show(5)
dept.show(5)
spark.stop()
