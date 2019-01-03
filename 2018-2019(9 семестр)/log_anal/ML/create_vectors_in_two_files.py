from ML import create_vectors

TRAINING = int(create_vectors.PERIOD*0.7)
TESTING = int(create_vectors.PERIOD*0.7)


class CreateVectorsApart(create_vectors.CreateVectors):
    def run(self, bad_users):
        self.up_data()

        # обучающая выбока
        path = "TRAINING.csv"
        print('user ' + self.user + ' start writing')
        self.write_in_csv(self.user, path, training_period=TRAINING, num_file=1)
        print('user ' + self.user + ' success writing')

        for i in bad_users:
            print('user ' + i + ' start writing')
            self.write_in_csv(i, path, training_period=TRAINING, num_file=1)
            print('user ' + i + ' success writing')

        # выборка для тестирования
        path = "TESTING.csv"
        print('user ' + self.user + ' start writing')
        self.write_in_csv(self.user, path, training_period=TRAINING, num_file=2)
        print('user ' + self.user + ' success writing')

        for i in bad_users:
            print('user ' + i + ' start writing')
            self.write_in_csv(i, path, training_period=TRAINING, num_file=2)
            print('user ' + i + ' success writing')
