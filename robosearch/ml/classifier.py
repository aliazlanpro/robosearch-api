"""
Lightweight classifier class for linear models trained elsewhere

Loads 'npz' files, which contain the model coefficients and
intercepts in sparse (csr) format. This allows very large models
(often several gigabytes in memory uncompressed) to be loaded
reasonably quickly, and makes for feasible memory usage.
"""

# Authors:  Iain Marshall <mail@ijmarshall.com>
#           Joel Kuiper <me@joelkuiper.com>
#           Byron Wallace <byron.wallace@utexas.edu>

import numpy as np
import logging
log = logging.getLogger(__name__)


class MiniClassifier:
    """
    Lightweight classifier
    Does only binary prediction using externally trained data
    """
    def __init__(self, filename):
        '''
        Loads a scikit-learn classifier from disk that has
        been converted to this miniature format
        '''
        log.debug("Loading model {}...".format(filename))
        with np.load(filename, encoding='latin1', allow_pickle=True) as raw_data:
            self.coef = raw_data["coef"].item().todense().A1
            self.intercept = raw_data["intercept"].item()

        log.debug("Model {} loaded".format(filename))

    def decision_function(self, X):
        scores = X.dot(self.coef.T) + self.intercept
        return scores

    def predict(self, X):
        scores = self.decision_function(X)
        return (scores>0).astype(np.int)

    def predict_proba(self, X):
        '''
        Note! This really only makes sense if the objective 
        for estimating w included a log-loss! Otherwise need 
        to calibrate.
        '''
        def sigmoid(z):
            s = 1.0 / (1.0 + np.exp(-1.0 * z))
            return s
        scores = self.decision_function(X)
        return sigmoid(scores)

class MiniOneVsAllClassifier():
    """
    Wraps a bunch of mini classifiers to do One vs All
    """
    def __init__(self, filenames, classes):
        self.classes = classes
        self.clfs = [MiniClassifier(f) for f in filenames]

    def decision_function(self, X):
        """
        run the X through all the included models
        """
        return np.array([clf.decision_function(X) for clf in self.clfs])

    def predict(self, X):
        """
        Get the highest scoring
        """
        scores = self.decision_function(X)
        return np.array([self.classes[i] for i in np.argmax(scores, axis=0)])

def main():
    pass


if __name__ == '__main__':
    main()
