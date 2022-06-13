from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier

class TrainModule:
    def __init__(self):
        self.clf = GradientBoostingClassifier()
        self.count_vec = TfidfVectorizer(input='train', stop_words={'english'}, lowercase=True, analyzer='word')
        self.tfidf_transformer = TfidfTransformer()

    def train(self, X_train, y_train): 
        train_vectors = self.count_vec.fit_transform(X_train)
        train_tdidf = self.tfidf_transformer.fit_transform(train_vectors)
        print("start training...")
        self.clf = self.clf.fit(train_tdidf, y_train)

    def predict(self, X_test, y_test):
        output = []
        for i in range(len(X_test)):
            test_vectors = self.count_vec.transform([X_test[i]])
            test_tfidf = self.tfidf_transformer.transform(test_vectors)
            predicted = self.clf.predict(test_tfidf)
            output.append(predicted)
        return output
        # print('accuracy: ', cal_accuracy(output, y_test))
        # print('precision: ', cal_precision(output, y_test))
        # print('recall: ', cal_recall(output, y_test))
        # print('f1: ', 2*cal_precision(output, y_test)*cal_recall(output, y_test)/(cal_precision(output, y_test)+cal_recall(output, y_test)))