"""나만의 퀴즈 게임 - 터미널에서 동작하는 4지선다 퀴즈 프로그램."""

LINE = "=" * 40


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
