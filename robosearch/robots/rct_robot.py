import os
import json
import numpy as np

import robosearch
from robosearch.ml.classifier import MiniClassifier
from sklearn.feature_extraction.text import HashingVectorizer
from scipy.sparse import lil_matrix, hstack

class RCTRobot:
    def __init__(self):
        self.svm_clf = MiniClassifier(os.path.join(robosearch.DATA_ROOT, 'rct/rct_svm_weights.npz'))
        self.svm_vectorizer = HashingVectorizer(binary=False, ngram_range=(1, 1), stop_words='english')
        with open(os.path.join(robosearch.DATA_ROOT, 'rct/rct_model_calibration.json'), 'r') as f:
            self.constants = json.load(f)

    def _process_ptyp(self, data_row, strict=True):
        """
        Takes in a data row which might include rct_ptyp
        or ptyp fields.

        If strict=True, then raises exception when passed any
        contradictory data

        Returns: 
        - 1 = ptyp is RCT 
        - 0 = ptyp is NOT RCT 
        - -1 = no ptyp information present 
        """
        if data_row['use_ptyp'] == False:
            return -1
        elif data_row['use_ptyp'] == True:
            return 1 if any((tag in data_row['ptyp'] for tag in ["randomized controlled trial", "Randomized Controlled Trial", "D016449"])) else 0
        elif strict:
            raise Exception("unexpcted value for 'use_ptyp'")

    def predict(self, X, filter_class="svm", filter_type="sensitive", auto_use_ptyp=True, raw_scores=False):


        if isinstance(X, dict):
            X = [X]

        if auto_use_ptyp:
            pt_mask = np.array([self._process_ptyp(r) for r in X])
        else:
            # don't add for any of them
            pt_mask = np.array([-1 for r in X])

        preds_l = {}

                # calculate ptyp for all
        #ptyp = np.copy(pt_mask)
        # ptyp = np.array([(article.get('rct_ptyp')==True)*1. for article in X])
        ptyp_scale = (pt_mask - self.constants['scales']['ptyp']['mean']) / self.constants['scales']['ptyp']['std']
        # but set to 0 if not using
        ptyp_scale[pt_mask==-1] = 0
        preds_l['ptyp'] = ptyp_scale

                # thresholds vary per article
        thresholds = []
        for r in pt_mask:
            if r != -1:
                thresholds.append(self.constants['thresholds']["{}_ptyp".format(filter_class)][filter_type])
            else:
                thresholds.append(self.constants['thresholds'][filter_class][filter_type])

        X_ti_str = [article.get('title', '') for article in X]
        X_ab_str = ['{}\n\n{}'.format(article.get('title', ''), article.get('abstract', '')) for article in X]

        if "svm" in filter_class:
            X_ti = lil_matrix(self.svm_vectorizer.transform(X_ti_str))
            X_ab = lil_matrix(self.svm_vectorizer.transform(X_ab_str))
            svm_preds = self.svm_clf.decision_function(hstack([X_ab, X_ti]))
            svm_scale =  (svm_preds - self.constants['scales']['svm']['mean']) / self.constants['scales']['svm']['std']
            preds_l['svm'] = svm_scale
            preds_l['svm_ptyp'] = preds_l['svm'] + preds_l['ptyp']

        preds_d =[dict(zip(preds_l,i)) for i in zip(*preds_l.values())]

        out = []

        if raw_scores:
            return {"svms": svm_preds,
                    "ptyps": pt_mask}

        else:

            for pred, threshold, used_ptyp in zip(preds_d, thresholds, pt_mask):
                row = {}
                if used_ptyp != -1:
                    row['model'] = "{}_ptyp".format(filter_class)
                else:
                    row['model'] = filter_class
                row['score'] = float(pred[row['model']])
                row['threshold_type'] = filter_type
                row['threshold_value'] = float(threshold)
                row['is_rct'] = bool(row['score'] >= threshold)
                row['ptyp_rct'] = int(used_ptyp)
                row['preds'] = {k: float(v) for k, v in pred.items()}
                out.append(row)
            return out