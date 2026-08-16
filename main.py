"""나만의 퀴즈 게임 - 터미널에서 동작하는 4지선다 퀴즈 프로그램.

[설계 요약]
- Quiz     : 문제 한 개의 데이터(문제/선택지/정답/힌트)와 그에 대한 동작(출력·채점·변환)을 담당
- QuizGame : 퀴즈 목록과 점수 등 '게임 상태'를 들고 메뉴 흐름을 진행

입력 검증(input_int/input_text) · 게임 진행(play_quiz/ask_one) · 저장 복원(load_state/save_state)을
서로 다른 메서드로 분리해, 요구사항이 바뀌어도 고칠 지점이 한 곳으로 모이도록 했다.

- 저장 시점 : 데이터가 바뀐 직후 state.json(UTF-8)에 기록해 강제 종료에도 유실되지 않게 한다.
- 예외 처리 : 사용자 입력·파일 입출력처럼 통제할 수 없는 지점에만 try/except를 둔다.
"""

import json                       # 파이썬 값 <-> JSON 글자 변환
import os                         # 파일이 있는지 확인 / 경로 만들기
import random                     # 퀴즈를 무작위로 뽑기
from datetime import datetime     # 게임한 날짜·시간 기록

LINE = "=" * 40           # "=" 를 40번 반복 -> 굵은 구분선
THIN_LINE = "-" * 40      # 얇은 구분선. 길이를 한 곳에서만 고치려고 변수로 뺐다

HINT_CHOICE = 5    # 정답 입력창에서 힌트를 요청하는 번호
HINT_PENALTY = 5   # 힌트를 1회 사용할 때 차감되는 점수
# 위 두 값은 뜻이 다른데 숫자가 같다. 코드에 5를 그냥 박아두면 하나를 고칠 때 다른 것까지 바뀌므로 이름을 붙였다.

# 데이터 파일은 프로젝트 루트(main.py와 같은 위치)의 state.json으로 고정한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


class Quiz:                                    # 문제 '한 장'. 데이터와 그 데이터로 하는 일을 한 덩어리로 묶는다
    """개별 퀴즈 한 문제를 표현하는 클래스."""

    def __init__(self, question, choices, answer, hint=""):   # 문제 하나를 만들 때 자동으로 실행된다
        self.question = question    # 문제 (str)          · self. = 이 문제 자신의
        self.choices = choices      # 선택지 4개 (list)
        self.answer = answer        # 정답 번호 1~4 (int)
        self.hint = hint            # 힌트 (str)  · hint="" 라서 힌트를 안 줘도 만들어진다
        # 정보 4개를 따로 두면 문제 수만큼 변수가 늘어나서 한 덩어리로 묶음

    def display(self, number):                 # 화면에 '보여주기'만 담당 - 채점과 섞지 않는다
        """문제와 선택지를 화면에 출력한다."""
        print(THIN_LINE)
        print(f"[문제 {number}]")               # f"..." = 문장 속에 값을 끼워 넣는 문법
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):   # enumerate = 값과 번호를 같이 꺼냄
            print(f"{index}. {choice}")                          # start=1 - 사람은 1번부터 세니까
        print()

    def check(self, selected):                 # 정답을 아는 건 이 문제 자신뿐 - 부르는 쪽은 정답을 몰라도 된다
        """입력한 번호가 정답인지 True/False로 돌려준다."""
        return selected == self.answer         # == 는 '같은가?' 비교 -> True 또는 False

    def to_dict(self):                         # 객체 -> 딕셔너리. 파일에 적으려면 글자로 바꿀 수 있는 모양이어야 한다
        """JSON 저장을 위해 딕셔너리로 변환한다."""
        return {
            "question": self.question,         # 칸 이름을 속성 이름과 똑같이 맞춰서
            "choices": self.choices,           # 옮길 때 대조표가 필요 없게 했다
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod                               # 객체가 아니라 '클래스'가 부르는 메서드 - 아직 객체가 없을 때 만들어 주는 역할
    def from_dict(cls, data):                  # 딕셔너리 -> 객체 (to_dict의 반대 방향)
        """JSON에서 읽은 딕셔너리를 Quiz 객체로 만든다."""
        return cls(
            data["question"],                  # 필수 칸 - 없으면 일부러 에러를 내서 load_state가 복구하게 둔다
            data["choices"],
            data["answer"],
            data.get("hint", ""),              # .get 은 칸이 없어도 안 죽고 "" 을 준다 (힌트 없던 옛날 파일 호환)
        )


def default_quizzes():                         # 데이터를 들고 있을 필요가 없어서 클래스가 아니라 그냥 함수로 뒀다
    """저장 파일이 없을 때 사용할 기본 퀴즈(파이썬 기초) 5개를 만들어 돌려준다."""
    return [                                   # 저장 파일이 없는 사람도 바로 5문제를 풀 수 있게 하려는 것
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


class QuizGame:                                # 게임 '진행'을 맡는다. 문제 내용은 모르고, 채점은 문제에게 시킨다
    """게임 전체(메뉴 흐름, 퀴즈 목록, 점수)를 관리하는 클래스."""

    def __init__(self):                        # 게임을 처음 켰을 때의 상태
        self.quizzes = default_quizzes()       # 저장 파일이 있으면 load_state가 곧 덮어쓴다
        self.best_score = 0
        self.history = []                      # [] = 빈 목록. 게임할 때마다 기록이 하나씩 쌓인다

    def show_menu(self):                       # 화면 출력만 담당 - 무엇을 실행할지는 run()이 정한다
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

    def load_state(self):                      # 파일 -> 메모리. 프로그램을 켤 때 딱 1번만 부른다
        """state.json에서 퀴즈와 점수를 불러온다. 없거나 손상되면 기본 퀴즈로 시작한다."""
        if not os.path.exists(STATE_FILE):     # 파일이 없는 건 오류가 아니라 '처음 실행'이다
            print(f"📂 저장된 데이터가 없어 기본 퀴즈로 시작합니다. (퀴즈 {len(self.quizzes)}개)")
            return                             # 그래서 에러 대신 기본 퀴즈로 그냥 시작한다

        try:                                   # 파일은 내가 만든 게 아니라 통제할 수 없으므로 try로 감싼다
            with open(STATE_FILE, "r", encoding="utf-8") as file:   # with = 다 쓰면 파일을 자동으로 닫아준다
                data = json.load(file)         # JSON 글자 -> 파이썬 딕셔너리          utf-8 = 한글이 안 깨지게
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]   # 읽은 것을 전부 Quiz 객체로
            self.best_score = data["best_score"]
            self.history = data["history"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:   # 실패 4가지를 한 번에 받아낸다
            print(f"⚠️ 저장 파일이 손상되어 기본 퀴즈로 복구합니다. ({error})")     # 죽는 대신 알려주고
            self.quizzes = default_quizzes()   # 기본 퀴즈로 되돌려 게임은 계속되게 한다
            self.best_score = 0
            self.history = []
        else:                                  # else = try가 '무사히' 끝났을 때만 실행되는 자리
            print(f"📂 저장된 데이터를 불러왔습니다. "
                  f"(퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")

    def save_state(self):                      # 메모리 -> 파일. 데이터가 바뀐 '직후'마다 부른다
        """현재 퀴즈 목록과 점수를 state.json에 UTF-8로 저장한다."""
        data = {                               # 저장할 모양을 먼저 만든다 (큰 칸 3개)
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],   # 객체는 그대로 못 적으니 딕셔너리로 변환
            "best_score": self.best_score,
            "history": self.history,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as file:   # "w" = 덮어쓰기 모드
                json.dump(data, file, ensure_ascii=False, indent=2) # ensure_ascii=False - 한글 그대로
        except OSError as error:                                    # indent=2 - 사람이 읽기 좋게 줄맞춤
            print(f"⚠️ 저장에 실패했습니다. ({error})")               # 디스크·권한 문제로 실패해도 게임은 계속되게

    def input_int(self, prompt, low, high):    # 숫자 입력 검사는 여기 한 곳에만 - 5곳에서 이 메서드를 부른다
        """low~high 범위의 정수를 입력받는다. 올바른 값이 들어올 때까지 반복한다."""
        while True:                            # 올바른 값이 들어올 때까지 계속 다시 묻는다
            value = input(prompt).strip()      # .strip() = 앞뒤 공백 제거 -> "  3" 도 3으로 받는다

            if value == "":                    # ① 빈 입력 검사
                print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue                       # continue = 아래로 안 가고 다시 물어보기

            try:
                number = int(value)            # ② 글자 검사 - "abc" 는 숫자로 못 바꿔서 여기서 걸린다
            except ValueError:
                print(f"⚠️ 숫자가 아닙니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue

            if number < low or number > high:  # ③ 범위 검사 - 없으면 random.sample이 죽는다
                print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue

            return number                      # 3단 검사를 모두 통과해야만 값을 돌려준다

    def input_text(self, prompt):              # 글자 입력용 - 빈 값만 막으면 되는 경우
        """빈 값이 아닌 문자열을 입력받는다."""
        while True:
            value = input(prompt).strip()
            if value == "":
                print("⚠️ 입력이 비어 있습니다. 내용을 입력해 주세요.")
                continue
            return value

    def add_quiz(self):                        # 퀴즈 추가 -> 곧바로 저장
        """새로운 퀴즈를 입력받아 목록에 추가하고 파일에 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.\n")

        question = self.input_text("문제를 입력하세요: ")
        choices = []
        for number in range(1, 5):             # range(1, 5) = 1,2,3,4 - 선택지 4개를 순서대로 받는다
            choices.append(self.input_text(f"선택지 {number}: "))
        answer = self.input_int("정답 번호 (1-4): ", 1, 4)   # 검사는 input_int가 대신 해 준다

        self.quizzes.append(Quiz(question, choices, answer))
        self.save_state()                      # 바뀐 직후 저장 - 강제 종료돼도 잃지 않게
        print("\n✅ 퀴즈가 추가되었습니다!")

    def list_quizzes(self):                    # 목록 출력. delete_quiz도 이 메서드를 다시 쓴다
        """저장된 퀴즈 목록을 번호와 함께 출력한다."""
        if not self.quizzes:                   # 파이썬은 '빈 목록'을 거짓으로 본다 -> not 을 붙이면 "비었다면"
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return                             # return = 이 기능만 끝내고 메뉴로 (프로그램 종료가 아니다)

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)\n")   # len() = 개수 세기
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print(THIN_LINE)

    def delete_quiz(self):                     # 삭제 -> 곧바로 저장
        """번호를 입력받아 해당 퀴즈를 목록에서 지우고 파일에 반영한다."""
        if not self.quizzes:
            print("\n⚠️ 삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()                    # 지우기 전에 목록을 보여줘야 번호를 고를 수 있다
        number = self.input_int(               # 범위를 1~(있는 개수)로 막아 없는 번호를 못 고르게 한다
            f"삭제할 퀴즈 번호 (1-{len(self.quizzes)}): ", 1, len(self.quizzes)
        )
        removed = self.quizzes.pop(number - 1) # 사람은 1번부터, 파이썬은 0번부터 세기 때문에 -1
        self.save_state()
        print(f"\n🗑️ 삭제되었습니다: {removed.question}")

    def ask_one(self, quiz, number):           # 문제 '하나'만 담당. 여러 문제 흐름은 play_quiz가 맡는다
        """문제 하나를 출제한다. (정답 여부, 힌트 사용 여부)를 돌려준다."""
        quiz.display(number)                   # 출력은 문제 자신에게 시킨다
        hint_used = False                      # 이 문제에서 힌트를 썼는지 표시

        while True:                            # 힌트(5번)를 누르면 아직 답이 아니므로 다시 묻는다
            selected = self.input_int(
                f"정답 입력 (1-4, 힌트 보기는 {HINT_CHOICE}): ", 1, HINT_CHOICE
            )
            if selected != HINT_CHOICE:        # 1~4를 골랐으면 답이므로 반복 탈출
                break
            if not quiz.hint:
                print("💡 이 문제에는 힌트가 없습니다.")
            else:
                print(f"💡 힌트: {quiz.hint} (힌트 사용 시 {HINT_PENALTY}점 차감)")
                hint_used = True

        if quiz.check(selected):               # 채점은 문제에게 물어본다 - 여기서는 정답을 모른다
            print("✅ 정답입니다!\n")
            return True, hint_used             # 값 2개를 한 번에 돌려준다 (맞았나, 힌트 썼나)

        answer_text = quiz.choices[quiz.answer - 1]   # 정답 '번호'로 실제 글자를 꺼낸다
        print(f"❌ 오답입니다! 정답은 {quiz.answer}번 ({answer_text})\n")   # 번호와 내용을 함께 알려준다
        return False, hint_used

    def play_quiz(self):                       # 한 판 전체 진행 (문제 하나하나는 ask_one에게 맡긴다)
        """퀴즈를 랜덤 순서로 출제하고 결과를 보여준다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        available = len(self.quizzes)          # 개수를 아래 3곳에서 쓰므로 한 번만 세서 담아둔다
        print(f"\n📝 등록된 퀴즈는 총 {available}문제입니다.")
        total = self.input_int(f"몇 문제를 푸시겠습니까? (1-{available}): ", 1, available)

        selected_quizzes = random.sample(self.quizzes, total)   # sample = 중복 없이 뽑기
        print(f"\n📝 퀴즈를 시작합니다! (총 {total}문제)\n")      # choice를 반복하면 같은 문제가 또 나온다

        correct = 0                            # 채점표는 반복문 '밖'에서 0으로 시작해야 한다
        hint_count = 0                         # 안에 두면 문제마다 0으로 초기화돼 항상 1점이 된다
        for number, quiz in enumerate(selected_quizzes, start=1):
            is_correct, hint_used = self.ask_one(quiz, number)   # 돌려받은 값 2개를 각각 담는다
            if is_correct:
                correct += 1                   # += 1 은 "1 더하기" (채점표에 정(正) 자 긋기)
            if hint_used:
                hint_count += 1

        score = max(0, round(correct / total * 100) - hint_count * HINT_PENALTY)   # max(0, ...) - 0점 밑으로 안 내려가게
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if hint_count > 0:
            print(f"   └ 힌트 {hint_count}회 사용 → {hint_count * HINT_PENALTY}점 차감")
        if self.record_result(total, correct, score):   # 기록 남기기는 따로 떼어냈다
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)

    def record_result(self, total, correct, score):   # 기록 + 최고점 갱신. play_quiz에서 떼어내 역할을 나눴다
        """게임 기록을 남기고 최고 점수를 갱신한다. 최고 점수를 새로 썼으면 True."""
        self.history.append({                  # append = 목록 뒤에 하나 붙이기
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),   # 사람이 읽는 날짜 형식으로
            "total": total,
            "correct": correct,
            "score": score,
        })

        is_best = score > self.best_score      # 신기록인지 먼저 판단하고
        if is_best:
            self.best_score = score            # 맞으면 최고점을 갈아치운다
        self.save_state()                      # 바뀐 직후 저장
        return is_best                         # 부른 쪽이 "신기록!" 을 띄울지 결정하게 True/False를 준다

    def show_score(self):                      # 보여주기만 담당 - 점수를 바꾸지 않는다
        """최고 점수와 지금까지의 게임 기록을 보여준다."""
        if not self.history:
            print("\n⚠️ 아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요.")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점")
        print(f"\n📜 최근 기록 (전체 {len(self.history)}회)")
        print(THIN_LINE)
        for record in self.history[-5:]:       # [-5:] = 뒤에서 5개만. 기록이 쌓여도 화면이 안 넘친다
            print(f"{record['date']} | {record['total']}문제 중 "
                  f"{record['correct']}문제 정답 | {record['score']}점")
        print(THIN_LINE)

    def run(self):                             # 메뉴 흐름만 담당 - 실제 일은 각 메서드에게 넘긴다
        """메뉴를 반복 출력하며 사용자의 선택에 따라 기능을 실행한다."""
        while True:                            # 기능이 끝나면 메뉴로 되돌아오게 하는 장치
            self.show_menu()
            choice = self.input_int("선택: ", 1, 6)   # 1~6 밖의 값은 여기서 다 걸러진다

            if choice == 1:                    # if / elif = 여러 갈림길 중 맞는 것 하나만 실행
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
                break                          # 무한 반복에서 나가는 문은 6번 하나뿐이다


def main():                                    # 프로그램이 시작되는 단 하나의 입구
    """프로그램 진입점."""
    game = QuizGame()
    game.load_state()                          # ① 먼저 파일에서 불러오고
    try:
        game.run()                             # ② 게임을 진행한다
    except (KeyboardInterrupt, EOFError):      # Ctrl+C(강제 중단) / EOF(입력이 끊김)
        # Ctrl+C 또는 입력 스트림 종료로 중단되어도 비정상 종료하지 않는다.
        print("\n\n⚠️ 입력이 중단되었습니다. 저장 후 안전하게 종료합니다.")   # 빨간 오류 대신 안내를 띄우고
        game.save_state()                      # 공책은 챙겨서 나간다


if __name__ == "__main__":                     # 이 파일을 직접 실행할 때만 main()을 부른다
    main()                                     # (다른 파일이 import 할 때는 실행되지 않게)
