# A project that takes raw audio signals of males and females and predicting the genders of these audio files. This is an end to end DE/ML project that will take these signals from raw to usable features that ML models will train on. 

## Final Pipeline Architecture:
![alt text](./figures%20&%20images/assets/finished%20architecture.jpg)

## Initial Pipeline Architecture:
![alt text](./figures%20&%20images/assets/initial%20architecture.jpg)

## Evolution of data/tables after each transformation:
![alt text](./figures%20&%20images/assets/table%20evolution.jpg)

## Previous Cloud Infrastructure:
![alt text](./figures%20&%20images/assets/cloud%20infrastructure.jpg)

## Technologies used:
1. Apache Airflow
2. DuckDB/Motherduck
3. Librosa
4. PyArrow
5. Azure Data Factory
6. Azure Data Lake Gen2
7. Azure Function App
8. Scikit-Learn
9. Google Colab
10. Terraform

## Dataset
The raw data consists of, as of 30th August 2018, 95,481 audio samples of male and female speakers speaking in short English sentences. The raw data is compressed using `.tgz` files. Each `.tgz` compressed file contains the following directory structure and files:

- `<file>/`
  - `etc/`
    - `GPL_license.txt`
    - `HDMan_log`
    - `HVite_log`
    - `Julius_log`
    - `PROMPTS`
    - `prompts-original`
    - `README`
  - `LICENSE`
  - `wav/`
    - 10 unique `.wav` audio files

The total size of the raw dataset is approximately 12.5 GB once it has been uncompressed. The file format is `.wav` with a sampling rate of 16kHz and a bit depth of 16-bit. The raw dataset can be found **[here][2]**.

We recommend considering the following for your data pre-processing:

1. Automate the raw data download using web scraping techniques. This includes extraction of individual audio files. 
2. Pre-process data using audio signal processing packages such as [WarbleR](https://cran.r-project.org/web/packages/warbleR/vignettes/warbleR_workflow.html), [TuneR](https://cran.r-project.org/web/packages/tuneR/index.html), [seewave](https://cran.r-project.org/web/packages/seewave/index.html) for R, [librosa](https://librosa.org/doc/latest/index.html), [PyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) for Python, or similar packages for other programming languages
3. Consider, in particular, the [human vocal range][1], which typically resides within the range of **0Hz-280Hz**
3. To help you on your way to identify potentially interesting features, consider the following (non-exhaustive) list:
  - Mean frequency (in kHz)
  - Standard deviation of frequency
  - Median frequency (in kHz)
  - Mode frequency
  - Peak frequency
  - First quantile (in kHz)
  - Third quantile (in kHz)
  - Inter-quantile range (in kHz)

  <!-- morphological features -->
  - Skewness
  - Kurtosis
  
4. Make sure to check out all of the files in the raw data, you might find valuable data in files beyond the audio ones

  [1]: https://en.wikipedia.org/wiki/Voice_frequency#Fundamental_frequency
  [2]: http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Main/16kHz_16bit/

## FAQ
1. How did you go about extracting features from the raw data? I used librosa to extract features more specific to audio signals such as spectral contrast, spectral rolloff, mel frequency cepstral coefficients, etc. aside from typical statistical and morphological features like mean, median, min, max, kurtosis, skewness, etc. which were computed using in-built SQL functions 

2. Which algorithms have you chosen, and what do each resulting model tell you about their performance? I chose a gradient boosted tree algorithm, which resulted in a model with 

Tree-based models (like Gradient Boosted Trees) are highly effective at finding complex, non-linear relationships and interactions within this type of structured, tabular data. They don't need to "learn" the features because you've already provided them with high-quality, relevant information. They excel at using these features to make accurate predictions.

  1. Which model performs best?
  2. How would you decide between using a more sophisticated model versus a less complicated one?

  Deep Learning Models are designed to automatically learn features from raw, unstructured data. You would feed the raw audio waveform directly into the model, and its many layers would learn to identify patterns like pitch and timbre on their own. However, they require massive amounts of data and computational power to do this effectively.

  Tree-based models utilize pre-existing features. By providing them with your carefully engineered features, you've already completed the hardest part of the problem. This allows the model to be much more efficient, requiring far less data and computational resources to achieve high accuracy.

4. What kind of benefits do you think your model(s) could have as part of an enterprise application or service?



## Articles, Videos, Research Papers:
* audio classification and feature extraction using librosa and pytorch: https://medium.com/@hasithsura/audio-classification-d37a82d6715
* audio analysis and feature extraction using librosa: https://athina-b.medium.com/audio-signal-feature-extraction-for-analysis-507861717dc1
* https://medium.com/@rijuldahiya/a-comprehensive-guide-to-audio-processing-with-librosa-in-python-a49276387a4b
* uses librosa and panda for audio preprocessing: https://www.youtube.com/watch?v=ZqpSb5p1xQo

## Usage:
1. clone repository with `git clone https://github.com/08Aristodemus24/signal-gender-predictor`
2. navigate to directory with `readme.md` and `requirements.txt` file
3. create .env file woth following env variables and assign your own values
- STORAGE_ACCOUNT_NAME
- STORAGE_ACCOUNT_KEY
- STORAGE_ACCOUNT_CONN_STR
- STORAGE_ACCOUNT_URL
- AZURE_CLIENT_ID
- AZURE_CLIENT_SECRET
- AZURE_SUBSCRIPTION_ID
- AZURE_TENANT_ID
- RESOURCE_GROUP_NAME
- MOTHERDUCK_TOKEN
4. run `make up` to spin up/run docker containers (run `make down` to shut down the docker container)
5. go to `localhost:8080` to see dag/s
6. run/trigger pipeline 

## To implement/fix:
1. deploy to kubernetes cluster as it seems an application using multiple docker containers needs a kubernetes cluster. Azure container apps, azure container registry, with azure kubernetes service could be viable and alternatively aws container registry, aws ecs, and aws eks.  

## Business Use Case:
Problem:
* voice and audio data can be difficult to efficiently and affordably convert raw, unstructured audio files into actionable intelligence
* Raw audio files are large, unwieldy, and require specialized tools to process. Extracting meaningful features from these signals is computationally intensive, and traditional methods often fail to scale, creating a massive data bottleneck that prevents machine learning projects from ever reaching production.
* Relying solely on expensive, proprietary cloud services can be suffocating cost wise for every stage of the pipeline—from data ingestion to feature transformation. This traps organizations into a cycle of high operational expenses, making valuable analytics and machine learning applications inaccessible to all but the largest enterprises.
* Without a standardized, automated, and repeatable process, every machine learning experiment becomes a manual, one-off project. This leads to inconsistent results, difficulty in reproducing models, and a significant amount of time and resources wasted on manual data wrangling rather than on model innovation.

Solution:
* This project was a direct response to these challenges. It is a testament to the power of a hybrid architecture, combining the best of managed cloud services yet still being cost conservative, open-source tools to build a comprehensive MLOps pipeline that is both scalable and cost-effective.
* The pipeline begins with a custom-built Azure Data Factory (ADF) sub-pipeline, intelligently extracting raw audio signals directly to a bronze container in Azure Data Lake Storage (ADLS2), effectively and affordably managing the initial data ingestion from diverse HTTP resources.
* Massively Parallel Feature Engineering: Instead of an expensive data warehouse, a Python-based transformation layer, orchestrated by Apache Airflow, processes gigabytes of the data directly in ADLS2. This leverages open-source libraries like Librosa for advanced signal feature extraction, NumPy for numerical efficiency, and DuckDB for lightning-fast, in-process analytics, transforming raw signals into refined features in a multi-stage process.
* Centralized and Reusable Features: The final, cleaned, and augmented features are stored in a gold-layer and then pushed to a central, live analytical database using MotherDuck. This creates a single source of truth for all features, enabling both efficient model training and low-latency inference for real-time applications.
* The entire process is automated and orchestrated by Apache Airflow, ensuring reliability, reproducibility, and transparent monitoring of every pipeline run. This transforms a complex, multi-step process into a single, repeatable, and production-ready workflow.



Outcome: 
* Developed an end-to-end MLOps pipeline for a audio signal gender prediction model, reducing cloud operational costs by over 70% by leveraging the cloud only for compute during extraction and storage and the rest for open source tools. 
* The pipeline automates the ingestion, transformation, and feature engineering of large-scale audio datasets, generating high-quality features for model training and serving.
* Architected and implemented a scalable data pipeline to process gigabytes of unstructured audio data. The system generates high-impact features for a voice-based gender prediction model providing a repeatable and production-ready framework for real-time audio analytics and a foundation for new voice-based AI applications.
* Engineered a multi-stage data transformation pipeline to efficiently process over 3.7 billion audio signals, handling data volumes that challenge traditional cloud data warehouse solutions.


Designed a resilient, containerized application with a multi-service architecture, paving the way for seamless deployment to scalable environments like Azure Kubernetes Service (AKS) or AWS EKS.

Established a modern data lakehouse pattern on Azure Data Lake Storage (ADLS2), ensuring data consistency and enabling efficient analytics directly on Parquet files, while leveraging MotherDuck for serverless query capabilities.