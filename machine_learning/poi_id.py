# coding=utf8
#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
# exercised_stock_options, total_stock_value, salary, bonus
features_list = [
    'poi',
    'exercised_stock_options',
    'total_stock_value', 
    'bonus',
    # 'salary', 
    # 'from_this_person_to_poi_rate',
    # 'deferred_income',
    # 'long_term_incentive',
    # 'restricted_stock',
] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
for k in ["LOCKHART EUGENE E", "THE TRAVEL AGENCY IN THE PARK", "TOTAL"]:
    data_dict.pop(k)

### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict.copy()
for name, attrs in my_dataset.items():
    if attrs["from_messages"] != "NaN" \
        and attrs["from_messages"] \
        and attrs["from_this_person_to_poi"] != "NaN":
        attrs["from_this_person_to_poi_rate"] = 1.0 * attrs["from_this_person_to_poi"] / attrs["from_messages"]
    else:
        attrs["from_this_person_to_poi_rate"] = "NaN"
    if attrs["to_messages"] != "NaN" \
        and attrs["to_messages"] \
        and attrs["from_poi_to_this_person"] != "NaN":
        attrs["from_poi_to_this_person_rate"] = 1.0 * attrs["from_poi_to_this_person"] / attrs["to_messages"]
    else:
        attrs["from_poi_to_this_person_rate"] = "NaN"


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn.preprocessing import MinMaxScaler


# Provided to give you a starting point. Try a variety of classifiers.


from sklearn.naive_bayes import GaussianNB
# clf = GaussianNB()

from sklearn import tree
clf = tree.DecisionTreeClassifier(criterion="entropy", max_features=1, random_state=42)

# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.pipeline import Pipeline


# clf = Pipeline([
#     ('sc', MinMaxScaler()),
#     ("clf", KNeighborsClassifier(n_neighbors=4, weights='distance'))
#     ])

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
# from sklearn.cross_validation import train_test_split
# features_train, features_test, labels_train, labels_test = \
#     train_test_split(features, labels, test_size=0.3, random_state=42)


from tester import test_classifier

# 
test_classifier(clf, my_dataset, features_list, folds = 1000)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)