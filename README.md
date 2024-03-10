# MAGGIE
In order to systematically study the potential risks when users use multiple apps simultaneously, we proposed a semi-automatic system, called *MAGGIE*, to check whether the **authentication strength** of a given app can be weakened by other apps.
Our work is accepted in NDSS 2024. 

## Repo Structure

```
Maggie
|   bin_search_run_codes.py # Run model code through binary division for model checking
|   model_builder.py # Read the Excel file containing PII information to generate model code, i.e. NUSMV code
|   output_path.py # Process NUSMV output and format attack paths
|   output_real_path.py # Identify redundant attack paths
|   README.md
|   run_codes_to_get_paths.py # Run NuSMV code to obtain attack path output
|
\---Xhelper
        blacklist.txt
        blackPageList.txt 
        CompareAlgorithm.py # Page comparison algorithm
        config.py # used for configuration 
        debugUtils.py #  debug related
        Detector.py # Information matching related
        PageStorage.py # Classes used to store page data
        Runner.py # Device interaction related
        Scanner.py # Page exploration strategy
        SenseTree.py # Optimize the original page tree structure for better storage and comparison
        Utils.py 
```

