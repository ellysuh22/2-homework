"""나만의 퀴즈 게임 - 터미널에서 동작하는 4지선다 퀴즈 프로그램."""

LINE = "=" * 40
THIN_LINE = "-" * 40


class Quiz:
    """개별 퀴즈 한 문제를 표현하는 클래스."""

    def __init__(self, question, choices, answer, hint=""):
        self.question = question    # 문제 (str)
        self.choices = choices      # 선택지 4개 (list)
        self.answer = answer        # 정답 번호 1~4 (int)
        self.hint = hint            # 힌트 (str)

    def display(self, number):
        """문제와 선택지를 화면에 출력한다."""
        print(THIN_LINE)
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")
        print()

    def check(self, selected):
        """입력한 번호가 정답인지 True/False로 돌려준다."""
        return selected == self.answer

    def to_dict(self):
        """JSON 저장을 위해 딕셔너리로 변환한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """JSON에서 읽은 딕셔너리를 Quiz 객체로 만든다."""
        return cls(
            data["question"],
            data["choices"],
            data["answer"],
            data.get("hint", ""),
        )


class QuizGame:
    """게임 전체(메뉴 흐름, 퀴즈 목록, 점수)를 관리하는 클래스."""

    def __init__(self):
        self.quizzes = []
        self.best_score = 0
        self.history = []

    def show_menu(self):
        """메뉴 화면을 출력한다."""
        print()
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 퀴즈 삭제")
        print("5. 점수 확인")
        print("6. 종료")
        print(LINE)

    def input_int(self, prompt, low, high):
        """low~high 범위의 정수를 입력받는다. 올바른 값이 들어올 때까지 반복한다."""
        while True:
            value = input(prompt).strip()

            if value == "":
                print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue

            try:
                number = int(value)
            except ValueError:
                print(f"⚠️ 숫자가 아닙니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue

            if number < low or number > high:
                print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue

            return number

    def run(self):
        """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
        while True:
            self.show_menu()
            choice = self.input_int("선택: ", 1, 6)

            if choice == 6:
                print("\n👋 게임을 종료합니다. 안녕히 가세요!")
                break
            else:
                print("\n🚧 아직 준비 중인 기능입니다.")


def main():
    """프로그램 진입점."""
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
