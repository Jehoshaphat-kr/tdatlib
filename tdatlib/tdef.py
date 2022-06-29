
class labels(object):
    KB금융 = '105560'
    하나금융지주 = '086790'
    DGB금융지주 = '139130'
    신한지주 = '055550'
    기업은행 = '024110'
    BNK금융지주 = '138930'
    우리금융지주 = '316140'
    상상인 = '038540'

    @property
    def banks(self) -> list:
        return [
            self.KB금융,
            self.하나금융지주,
            self.DGB금융지주,
            self.신한지주,
            self.기업은행,
            self.BNK금융지주,
            self.우리금융지주,
            self.상상인
        ]