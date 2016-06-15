from preprocess.preparedata import PrepareData

from time import time
from evaluation.sklearnmape import mean_absolute_percentage_error
from utility.dumpload import DumpLoad
import numpy as np
from datetime import datetime
from utility.datafilepath import g_singletonDataFilePath
from evaluation.sklearnmape import mean_absolute_percentage_error_scoring
from sklearn import cross_validation
from utility.duration import Duration
import logging
from utility.logger_tool import Logger

class BaseModel(PrepareData):
    def __init__(self):
        PrepareData.__init__(self)
        self.setClf()
        self.application_start_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.save_final_model =False
        self.do_cross_val = True
#         logfile_name = r'logs//' + self.__class__.__name__+ '_' +self.application_start_time + '.txt'
#         _=Logger(filename=logfile_name,filemode='w',level=logging.DEBUG)
        self.durationtool = Duration()
        
        return
    def setClf(self):
        pass
    def after_train(self):
        pass
    def train(self):
        print "Training {}...".format(self.clf.__class__.__name__)
        t0 = time()
        self.clf.fit(self.X_train, self.y_train)
        print "train:", round(time()-t0, 3), "s"
        self.dispFeatureImportance()
        self.after_train()
        return
    def save_model(self):
        if not self.save_final_model:
            return
        dumpload = DumpLoad('logs/' + self.application_start_time + '_estimator.pickle')
        dumpload.dump(self)
        self.predictTestSet(g_singletonDataFilePath.getTest2Dir())
        return
    def dispFeatureImportance(self):
        if not hasattr(self.clf, 'feature_importances_'):
            return
        features_list = np.asanyarray(self.usedFeatures)
        sortIndexes = self.clf.feature_importances_.argsort()[::-1]
        features_rank = features_list[sortIndexes]
        num_rank = self.clf.feature_importances_[sortIndexes]
        print "Ranked features: {}".format(features_rank)
        print "Ranked importance: {}".format(num_rank)
        return
    def test(self):
        
        y_pred_train = self.clf.predict(self.X_train)
        y_pred_test = self.clf.predict(self.X_test)
        print "features used:\n {}".format(self.usedFeatures)
        print "MAPE for training set: {}".format(mean_absolute_percentage_error(self.y_train, y_pred_train))
        print "MAPE for testing set: {}".format(mean_absolute_percentage_error(self.y_test, y_pred_test))
#         print "MSE for training set: {}".format(mean_squared_error(self.y_train, y_pred_train))
#         print "MSE for testing set: {}".format(mean_squared_error(self.y_test, y_pred_test))
#         pd.DataFrame({'y_train':self.y_train.values, 'y_train_pred':y_pred_train}).to_csv('temp/trainpred.csv')
#         pd.DataFrame({'y_test':self.y_test.values, 'y_test_pred':y_pred_test}).to_csv('temp/testpred.csv')
        
        self.after_test()
        return
    def after_test(self):
        pass
    def predictTestSet(self, dataDir):
        X_y_Df= self.getFeaturesforTestSet(dataDir)
        y_pred = self.clf.predict(X_y_Df[self.usedFeatures])
        X_y_Df['y_pred'] = y_pred
        df = X_y_Df[['start_district_id', 'time_slotid', 'y_pred']]
        filename = 'logs/'+ self.application_start_time + '_gap_prediction_result.csv'
        df.to_csv(filename , header=None, index=None)
        
        return
    def get_train_validation_foldid(self):
        return -1
    def run_croos_validation(self):
        features,labels,cv = self.getFeaturesLabel()
        scores = cross_validation.cross_val_score(self.clf, features, labels, cv=cv, scoring=mean_absolute_percentage_error_scoring)
        print "cross validation scores: means, {}, std, {}, details,{}".format(np.absolute(scores.mean()), scores.std(), np.absolute(scores))
        return
    def run_train_validation(self):
        self.get_train_validationset(foldid= self.get_train_validation_foldid())
#         self.getTrainTestSet()
        self.train()
        self.test()
        self.save_model()
        return
    def run(self):
        t0 = time()
        if self.do_cross_val:
            self.run_croos_validation()
            print "test:", round(time()-t0, 3), "s"
            return
        self.run_train_validation()
        print "test:", round(time()-t0, 3), "s"
        return
    
if __name__ == "__main__":   
    obj= BaseModel()
    obj.run()