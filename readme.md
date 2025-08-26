# A project that takes raw audio signals of males and females and predicting the genders of these audio files. This is an end to end DE/ML project that will take these signals from raw to usable features that ML models will train on. 

## Pipeline Architecture:
![alt text](./figures%20&%20images/initial%20architecture.jpg)

## Cloud Infrastructure:
![alt text](./figures%20&%20images/initial%20architecture.jpg)
![alt text](<figures & images/initial architecture.jpg>)

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

## Question Set

The following are reference points that should be taken into account in the submission. Please use them to guide the reasoning behind the feature extraction, exploration, analysis and model building, rather than answer them point blank.

1. How did you go about extracting features from the raw data?
2. Which features do you believe contain relevant information?
  1. How did you decide which features matter most?
  2. Do any features contain similar information content?
  3. Are there any insights about the features that you didn't expect? If so, what are they?
  4. Are there any other (potential) issues with the features you've chosen? If so, what are they?
3. Which goodness of fit metrics have you chosen, and what do they tell you about the model(s) performance?
  1. Which model performs best?
  2. How would you decide between using a more sophisticated model versus a less complicated one?
4. What kind of benefits do you think your model(s) could have as part of an enterprise application or service?



## Articles, Videos, Research Papers:
* audio classification and feature extraction using librosa and pytorch: https://medium.com/@hasithsura/audio-classification-d37a82d6715
* audio analysis and feature extraction using librosa: https://athina-b.medium.com/audio-signal-feature-extraction-for-analysis-507861717dc1
* https://medium.com/@rijuldahiya/a-comprehensive-guide-to-audio-processing-with-librosa-in-python-a49276387a4b
* uses librosa and panda for audio preprocessing: https://www.youtube.com/watch?v=ZqpSb5p1xQo

## Usage:
1. clone repository with `git clone https://github.com/08Aristodemus24/signal-gender-predictor`
2. navigate to directory with `readme.md` and `requirements.txt` file
3. run command; `conda create -n <name of env e.g. signal-gender-predictor> python=3.11.8`. Note that 3.11.8 must be the python version otherwise packages to be installed would not be compatible with a different python version
4. once environment is created activate it by running command `conda activate`
5. then run `conda activate signal-gender-predictor`
6. check if pip is installed by running `conda list -e` and checking list
7. if it is there then move to step 8, if not then install `pip` by typing `conda install pip`
8. if `pip` exists or install is done run `pip install -r requirements.txt` in the directory you are currently in
9. when install is done assuming we are already in environment run `python download_data.py` to download `.tar` files
10. after all downloads have finished and script is finished run next `python extract_data.py` to uncompress `.tar` files and delete the unnecessary zip files after extraction. This will result in a data folder being created with all the subjects respective folders containing their audio recordings
11. run the `prepare_data` notebook as this will create the necessary files containing the features of the audio signals taken from the loaded raw audio signals
12. this will result in the creation of the `_EXTRACTED_DATA` folder in the data folder and in it will be two sub directories test and train containing the features for training and testing the model. Each sub directory contains the two categories of files for each subject: a feature file and a label files named `<name of subject>_features.csv` and `<name of subject>_labels.csv`. This we will concurrently load when training script is ran.
13. to train model run `python tuning_dl.py -m <name of model we want to use e.g. lstm list of models are listed in the dictionary object in the script> -c <the configuration we want our training to be e.g. deep (if we want to use a deep learning model and trad if we want a traditional ML model)> -lr <learning rate value e.g. 1e-3> --batch_size <batch size value e.g. 256> --mode <mode we want script to run on e.g. training> --hyper_param_list <a list of hyper parameters we use during training of our model separated by spaces with each value representing the hyper parameter we want to add and next to it its value separated by an underscore e.g. hertz_8000 window_time_0.25 hop_time_0.125 n_a_128 dense_drop_prob_0.2 rnn_drop_prob_0.2>`

some preset commands we can already use:
- `python tuning_dl.py -m lstm -c deep -lr 1e-3 --batch_size 256 --mode training --hyper_param_list hertz_8000 window_time_0.25 hop_time_0.125 n_a_128 dense_drop_prob_0.2 rnn_drop_prob_0.2` to train a sequential LSTM neural network model\
- `python tuning_dl.py -m softmax -c trad -lr 1e-3 --batch_size 256 --mode training --hyper_param_list hertz_8000 window_time_0.25 hop_time_0.125` to train a softmax regression model which will use the engineered features we have

14. screenshot of extracted features: 
![dataframes](./figures%20&%20images/Screenshot%202025-03-12%20143231.png)
![dataframes](./figures%20&%20images/Screenshot%202025-03-12%20140242.png)
15. screenshot of labels: 
![dataframes](./figures%20&%20images/Screenshot%202025-03-12%20143241.png)
![dataframes](./figures%20&%20images/Screenshot%202025-03-12%20140300.png)


15. you can run notebook visualization.ipynb to see performance metric values of the trained models 

## To implement/fix:
1. testing/evaluation script to use saved model weights to see overall test performance of model
2. there seems to be something wrong as the models seem to have loss go up during training and auc go down, which signifies the model may be underfitting, or not generalizing well on the training set. This may be because there aren't enough examples for the other class for the model to learn from and learns that the audio signals are mostly male voices, which we know in the dataset outweighs by large margin the female labeled audio recordings. Solution could be to gather more female recordings, and extract more features from it. Another less viable option is to undersample the male class so that it is equal to the amount of female audio signal inputs
3. hyper parameter tuning to determine more viable hyper parameters for each model
4. learn and try tensorflow decision forest models and see if if will be better than a typical softmax regression model
5. learn more about audio signal processing as I still don't know how to better extract features from audio signals without me fully understanding concepts like mel spectrograms, spectral centroids, etc.
6. solving why f1 score seems to bee a numpy array instead of a single value: https://stackoverflow.com/questions/68596302/f1-score-metric-per-class-in-tensorflow
7.  `: RESOURCE_EXHAUSTED: OOM when allocating tensor with shape[128,128] and type float on /job:localhost/replica:0/task:0/device:CPU:0 by allocator mklcpu 2025-03-12 16:17:33.380804: I tensorflow/core/framework/local_rendezvous.cc:405] Local rendezvous is aborting with status: RESOURCE_EXHAUSTED: OOM when allocating tensor with shape[256,128] and type float on /job:localhost/replica:0/task:0/device:CPU:0 by allocator mklcpu` this error may be due to the immense size of the input data which we know is (m, 2000, 1) and given we have 6815 subjects, which is incomparable to the previous project I did which only had 43 subjects at most, this preprocessing of the data for deep learning tasks, I might have to do with a better machine, or somehow interpolate the raw audio signals to a much lower frequency, which may unfortunately cause importatn features to be lost.
