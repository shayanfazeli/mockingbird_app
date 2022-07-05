# MOCKINGBIRD

*A subproject of [Project ReFOCUS](www.projectrefocus.com) and OLIVIA*


## Getting started
This software library is fully dockerized therefore you can follow the easy steps below to get started:


### 1. Prepring files and folders
Modify the `.env` file to the following:
* `ACCOUNTS_DF_FILEPATH`: the path to the `accounts.csv` which contains the twitter accounts used in this system.
* `TWEETS_ROOT`: the root repository of the dataset. Please note that, when you fetch the data, it gets stored as
`twitter_handle.csv` in each of its subfolders.
* `CACHE_FOLDERPATH`: an empty folder (or previously prepared folder) for cache.

#### Caching
Given the computational cost of many of the operations that are inevitable in this framework, each request's results
will be cached so that the request, upon next call, will be ready to serve and won't need recomputation.


### 2. Dockerize
First, refer to the Data section, and download `accounts.csv` as well as the data folders (folders including files such as `CNN.csv`).
Second, create a folder in your machine containing the following structure:

```
- accounts.csv
- tweets/folder1/CNN.csv
- tweets/folder2/CNN.csv
...
- tweets/folder3/CNN.csv
- cache/
```

Note that you need to create a `cache` folder as well. Once done, modify the
`.env` file to reflect on the changes.

Now, to finalize the dockerization follow the steps below:

* Create the image: `docker build --tag mockingbird .`
  * (if you want to delete an image, you can run `docker image rm image_name`)
* Create the volume: `docker volume create --driver local --name volume_name --opt device=path_to_folder_on_host --opt o=uid=root,gid=root --opt o=bind --opt type=none`
* Run the image: `docker run -v refocus_drive:/container/warehouse -d -p 5000:5000 mockingbird`

__Remark__: You can use `docker system prune -a` to clean the unused images, etc.

docker image rm mockingbird --force; docker build --tag mockingbird .; docker run -v refocus_drive:/container/warehouse -d -p 5000:5000 mockingbird

docker system prune -a

## Data
### Details
The details of the accounts used in the current version of the dataset are available in [accounts.csv]().
If you have recommendations regarding adding twitter handles, please use [this form](https://forms.gle/JqGgxPWnAP1hZmUj7) to submit them to us.

### Download
Using the [mockingbird_download]() script provided in the source code, you can download the relevant data for a
custom time-period without the need for a Twitter API key.

#### Example:
```bash
python3 app/scripts/mockingbird_download.py \
--start_time="2022-01-01 16:30:00" \
--end_time="2022-03-01 16:30:00" \
--output_repo="/output_repo"
```

## Collaboration
Our dataset can be shared upon reasonable collaboration request. Please contact [shayan@cs.ucla.edu](mailto:shayan@cs.ucla.edu).


## Citation
```

```