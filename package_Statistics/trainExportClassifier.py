# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Train and export multi-class classifier
# Author: Timm Nawrocki
# Last Updated: 2022-03-27
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Train and export multi-class classifier" is a function that trains and exports a classifier and a table of variable importance for a multi-class problem.
# ---------------------------------------------------------------------------

# Create a function to train and export a classification model
def train_export_classifier(classifier_params, input_data, class_variable, predictor_all, output_classifier):
    """
    Description: trains and exports a classification model and threshold value
    Inputs: 'classifier_params' -- a set of parameters for a random forest classifier specified according to the sklearn API
            'input_data' -- a data frame containing the class and covariate data
            'class_variable' -- the names of the field that contains the class labels
            'predictor_all' -- the names of the fields that contain covariate values
            'output_classifier' -- a joblib file to store the trained classifier
    Returned Value: Returns a trained classifier on disk and a table of variable importances in memory
    Preconditions: requires a classifier specification and a data frame of covariates and responses
    """

    # Import packages
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import time
    import datetime

    # Split the X and y data for classification
    X_classify = input_data[predictor_all].astype(float)
    y_classify = input_data[class_variable[0]].astype('int32')

    # Train classifier
    print('\tTraining full classifier...')
    iteration_start = time.time()
    # Train first set of trees with gini
    classifier_params['criterion'] = 'gini'
    outer_classifier_gini = RandomForestClassifier(**classifier_params)
    outer_classifier_gini.fit(X_classify, y_classify)
    # Train second set of trees with entropy
    classifier_params['criterion'] = 'entropy'
    outer_classifier_entropy = RandomForestClassifier(**classifier_params)
    outer_classifier_entropy.fit(X_classify, y_classify)
    # Train third set of trees with log_loss
    classifier_params['criterion'] = 'log_loss'
    outer_classifier_logloss = RandomForestClassifier(**classifier_params)
    outer_classifier_logloss.fit(X_classify, y_classify)
    # Combine models
    outer_classifier_gini.estimators_ = outer_classifier_gini.estimators_ + outer_classifier_entropy.estimators_ + outer_classifier_logloss.estimators_
    outer_classifier_gini.n_estimators = len(outer_classifier_gini.estimators_)
    export_classifier = outer_classifier_gini
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    print(
        f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t\t----------')

    # Save classifier to an external file
    joblib.dump(export_classifier, output_classifier)

    # Get feature importances calculated as MDI
    importances = export_classifier.feature_importances_
    feature_names = list(X_classify.columns)
    importance_table = pd.DataFrame({'covariate': feature_names,
                                     'importance': importances})

    # Return trained classifier
    return export_classifier, importance_table
