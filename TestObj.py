import unittest

from Obj import self.client

# тут будет производиться тестирование моего ПО, в целях убедиться, что
# случайных багов нет!
class Testself.client(unittest.TestCase):
    def setUp(self):
        # инициализация моего класса
        self.self.client = self.client("111")
        self.reg = self.self.client.registration
        # assertEqual(вызов функции со значениями, ожидаемый return)
        #- встроенный метод проверки соответствия ожидания и реальности

    def justtesting(self, func, returned):
        #self.self.client.registration() #шаблон, мы регистрируем его, делаем рповерку и удаляем
        self.assertEqual(func, returned)
        self.self.client.add_into_base(f"DELETE from users where userid = {self.self.client.id}")

    def test_registration(self):
        self.assertEqual(self.self.client.registration(test=True), "Added") # id 111 budget 10

        self.reg()
        self.justtesting(self.self.client.registration(), "Been")


    def test_get_budget(self):
        self.reg()
        self.justtesting(self.self.client.get_budget(), 10)


if __name__ == "__main__":
  unittest.main()
