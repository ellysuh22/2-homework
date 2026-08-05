"""나만의 퀴즈 게임 - 터미널에서 동작하는 4지선다 퀴즈 프로그램."""

import json
import os
import random
from datetime import datetime

LINE = "=" * 41
THIN_LINE = "-" * 40

HINT_CHOICE = 5    # 정답 입력창에서 힌트를 요청하는 번호
HINT_PENALTY = 5   # 힌트를 1회 사용할 때 차감되는 점수

# 데이터 파일은 프로젝트 루트(main.py와 같은 위치)의 state.json으로 고정한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


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


def default_quizzes():
    """저장 파일이 없을 때 사용할 기본 퀴즈(파이썬 기초) 5개를 만들어 돌려준다."""
    return [
        Quiz(
            "파이썬에서 리스트를 만들 때 사용하는 괄호는?",
            ["( )", "[ ]", "{ }", "< >"],
            2,
            "순서가 있고 나중에 값을 바꿀 수 있는 자료형에 쓰는 기호입니다.",
        ),
        Quiz(
            "다음 중 True와 False 두 가지 값만 가지는 자료형은?",
            ["int", "str", "bool", "list"],
            3,
            "조건문의 판단 결과로 나오는 자료형입니다.",
        ),
        Quiz(
            "클래스로 객체를 만들 때 자동으로 호출되는 메서드는?",
            ["__init__", "__main__", "__str__", "__name__"],
            1,
            "객체의 속성을 처음 초기화하는 생성자 역할을 합니다.",
        ),
        Quiz(
            "딕셔너리(dict)에서 값을 꺼낼 때 기준이 되는 것은?",
            ["인덱스 번호", "키(key)", "슬라이스", "저장한 순서"],
            2,
            "리스트와 달리 0, 1, 2 같은 번호를 쓰지 않습니다.",
        ),
        Quiz(
            "정해진 횟수만큼 반복할 때 주로 사용하는 반복문은?",
            ["while", "for", "if", "try"],
            2,
            "range()나 리스트와 함께 자주 쓰는 반복문입니다.",
        ),
    ]


class QuizGame:
    """게임 전체(메뉴 흐름, 퀴즈 목록, 점수)를 관리하는 클래스."""

    def __init__(self):
        self.quizzes = default_quizzes()
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

    def load_state(self):
        """state.json에서 퀴즈와 점수를 불러온다. 없거나 손상되면 기본 퀴즈로 시작한다."""
        if not os.path.exists(STATE_FILE):
            print(f"📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다. (퀴즈 {len(self.quizzes)}개)")
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            self.best_score = data["best_score"]
            self.history = data["history"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            print(f"⚠️ 저장 파일이 손상되어 기본 퀴즈로 복구합니다. ({error})")
            self.quizzes = default_quizzes()
            self.best_score = 0
            self.history = []
        else:
            print(f"📂 저장된 데이터를 불러왔습니다. "
                  f"(퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")

    def save_state(self):
        """현재 퀴즈 목록과 점수를 state.json에 UTF-8로 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"⚠️ 저장에 실패했습니다. ({error})")

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

    def input_text(self, prompt):
        """빈 값이 아닌 문자열을 입력받는다."""
        while True:
            value = input(prompt).strip()
            if value == "":
                print("⚠️ 입력이 비어 있습니다. 내용을 입력해 주세요.")
                continue
            return value

    def add_quiz(self):
        """새로운 퀴즈를 입력받아 목록에 추가하고 파일에 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")

        question = self.input_text("문제를 입력하세요: ")
        choices = []
        for number in range(1, 5):
            choices.append(self.input_text(f"선택지 {number}: "))
        answer = self.input_int("정답 번호 (1-4): ", 1, 4)

        self.quizzes.append(Quiz(question, choices, answer))
        self.save_state()
        print("\n✅ 퀴즈가 추가되었습니다!")

    def list_quizzes(self):
        """저장된 퀴즈 목록을 번호와 함께 출력한다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)\n")
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print(THIN_LINE)

    def delete_quiz(self):
        """번호를 입력받아 해당 퀴즈를 목록에서 지우고 파일에 반영한다."""
        if not self.quizzes:
            print("\n⚠️ 삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()
        number = self.input_int(
            f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}): ", 1, len(self.quizzes)
        )
        removed = self.quizzes.pop(number - 1)
        self.save_state()
        print(f"\n🗑️ 삭제되었습니다: {removed.question}")

    def ask_one(self, quiz, number):
        """문제 하나를 출제한다. (정답 여부, 힌트 사용 여부)를 돌려준다."""
        quiz.display(number)
        hint_used = False

        while True:
            selected = self.input_int(
                f"정답 입력 (1-4, 힌트 보기는 {HINT_CHOICE}): ", 1, HINT_CHOICE
            )
            if selected != HINT_CHOICE:
                break
            if not quiz.hint:
                print("💡 이 문제에는 힌트가 없습니다.")
            else:
                print(f"💡 힌트: {quiz.hint} (힌트 사용 시 {HINT_PENALTY}점 차감)")
                hint_used = True

        if quiz.check(selected):
            print("✅ 정답입니다!\n")
            return True, hint_used

        answer_text = quiz.choices[quiz.answer - 1]
        print(f"❌ 오답입니다! 정답은 {quiz.answer}번 ({answer_text})\n")
        return False, hint_used

    def play_quiz(self):
        """퀴즈를 랜덤 순서로 출제하고 결과를 보여준다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        available = len(self.quizzes)
        print(f"\n📝 등록된 퀴즈는 총 {available}문제입니다.")
        total = self.input_int(f"몇 문제를 푸시겠습니까? (1-{available}): ", 1, available)

        selected_quizzes = random.sample(self.quizzes, total)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)\n")

        correct = 0
        hint_count = 0
        for number, quiz in enumerate(selected_quizzes, start=1):
            is_correct, hint_used = self.ask_one(quiz, number)
            if is_correct:
                correct += 1
            if hint_used:
                hint_count += 1

        score = max(0, round(correct / total * 100) - hint_count * HINT_PENALTY)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if hint_count > 0:
            print(f"   └ 힌트 {hint_count}회 사용 → {hint_count * HINT_PENALTY}점 차감")
        if self.record_result(total, correct, score):
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)

    def record_result(self, total, correct, score):
        """게임 기록을 남기고 최고 점수를 갱신한다. 최고 점수를 새로 썼으면 True."""
        self.history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": total,
            "correct": correct,
            "score": score,
        })

        is_best = score > self.best_score
        if is_best:
            self.best_score = score
        self.save_state()
        return is_best

    def show_score(self):
        """최고 점수와 지금까지의 게임 기록을 보여준다."""
        if not self.history:
            print("\n⚠️ 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요.")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점")
        print(f"\n📜 최근 기록 (전체 {len(self.history)}회)")
        print(THIN_LINE)
        for record in self.history[-5:]:
            print(f"{record['date']} | {record['total']}문제 중 "
                  f"{record['correct']}문제 정답 | {record['score']}점")
        print(THIN_LINE)

    def run(self):
        """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
        while True:
            self.show_menu()
            choice = self.input_int("선택: ", 1, 6)

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.delete_quiz()
            elif choice == 5:
                self.show_score()
            else:
                print("\n👋 게임을 종료합니다. 안녕히 가세요!")
                break


def main():
    """프로그램 진입점."""
    game = QuizGame()
    game.load_state()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 또는 입력 스트림 종료로 중단되어도 비정상 종료하지 않는다.
        print("\n\n⚠️ 입력이 중단되었습니다. 저장 후 안전하게 종료합니다.")
        game.save_state()


if __name__ == "__main__":
    main()
