README
pipeline
#	check requirements.txt

Modify json file for wanted language pairs

1	scraper.ipynb	Scrape loanword pairs and homonyms

2	scraper_lemmas.ipynb	Scrape donor-language lemmas

Target directory for scraped files is "/notebooks/results"
------------------------------------------------------------------

3	make-datasets.ipynb	Generate positive and negative datasets

Datasets will be saved in Datasets directory (Loans, hard negatives, randoms, synonyms)
------------------------------------------------------------------------

4	remove-overlaps.ipynb	Remove overlapping examples

5	make-train-test-splits.ipynb	Create training and testing data
Will make splits in Datasets
-----------------------------------------------------------------------

6	get-logits-cos_sims.ipynb	Train alignment networks and calculate similarities
	data will be stored in Datasets/train_test_split overwriting data created in step 5
	or
	get_logits_cos_sims_colab 	if you are running the notebook on colab
	data will be downloaded from colab in new folder production_train_test_split
	
------------------------------------------------------------------------
7	evaluate-experiments.ipynb	Run the classifiers and evaluate results
	takes from the production_train_test folder in Datasets and makes Final_results folder where eval metrics are stored
	or
	evaluate-experiments-colab.ipynb to run in colab (faster)
	upload zip production_train_test_split and download each evaluation folder

Folder "old" has old datasets and extra scripts, that may come in use
