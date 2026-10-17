import re
import unicodedata
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import ArrayType, StringType
from technologies import TECHNOLOGIES


def normaliser(texte):
    texte = unicodedata.normalize("NFD", texte or "")
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()


MOTIFS = {t: re.compile(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])") for t in TECHNOLOGIES}


def extraire(titre, description):
    texte = normaliser((titre or "") + " " + (description or ""))
    return sorted(t for t, m in MOTIFS.items() if m.search(texte))


spark = SparkSession.builder.master("local[2]").appName("silver_competences").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

silver = spark.read.parquet("data/silver/offres")
extraire_udf = F.udf(extraire, ArrayType(StringType()))
res = silver.withColumn("competences_extraites", extraire_udf("titre", "description"))
res = res.withColumn("nb_competences", F.size("competences_extraites"))
res.write.mode("overwrite").parquet("data/silver/offres_competences")

print("Offres traitees :", res.count())
print("Offres avec au moins 1 competence :", res.filter("nb_competences > 0").count())
print("Competences par offre en moyenne :", res.agg(F.avg("nb_competences")).first()[0])
top = res.select(F.explode("competences_extraites").alias("technologie"))
top.groupBy("technologie").count().orderBy(F.desc("count")).show(15)
spark.stop()
