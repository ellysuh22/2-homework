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

    def run(self):
        """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
        while True:
            self.show_menu()
            choice = input("선택: ").strip()

            if choice == "6":
                print("\n👋 게임을 종료합니다. 안녕히 가세요!")
                break
            elif choice in ("1", "2", "3", "4", "5"):
                print("\n🚧 아직 준비 중인 기능입니다.")
            else:
                print("\n⚠️ 잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요.")


def main():
    """프로그램 진입점."""
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    main()
