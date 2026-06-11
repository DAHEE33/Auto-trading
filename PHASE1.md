# Phase 1 개발 계획서

## 📋 전체 개요

### 목표
텔레그램만으로 완전히 동작하는 MVP 서비스 구축  
**이 시점이 포트폴리오 제출 가능 시점**

### 기간
약 10주 (단계별 1~2주)

### 핵심 기능
1. **A. 오늘의 핫 종목 발굴** - AI Agent가 자동으로 경제 뉴스 분석 후 주목 종목 TOP 3 발굴
2. **B. 관심 종목 분석** - 사용자가 등록한 종목의 자동 분석 및 패턴 감지
3. **텔레그램 Bot** - 리포트 자동 발송 및 커맨드 처리
4. **주가 반응 추적** - 분석 결과와 실제 주가 변동 비교

### 기술 스택
- **Backend**: Java 17 + Spring Boot 3.x
- **AI**: LangChain4j (ReAct), OpenAI API (gpt-4o, gpt-4o-mini)
- **크롤링/수집**: Python + BeautifulSoup + FinanceDataReader
- **Database**: PostgreSQL (Docker)
- **Bot**: Telegram Bot API
- **배포**: Oracle Cloud + Docker Compose + GitHub Actions

---

## 🔧 단계별 상세 개발 계획

### **STEP 1-1: Python 뉴스 크롤러 구현**
**예상 기간**: 1주

#### 개발 목표
- RSS 피드 및 Jsoup을 이용한 뉴스 크롤링
- 원문 URL 포함한 뉴스 데이터 수집
- 중복 제거 로직 구현
- PostgreSQL DB 저장

#### 구체적 구현 내용
1. **뉴스 소스 설정**
   - 한국경제, 매일경제, 연합뉴스 등 주요 경제 뉴스 RSS 피드
   - 각 뉴스사별 크롤링 모듈 구현

2. **크롤링 로직**
   ```
   - RSS 피드에서 기사 목록 수집
   - 각 기사의 원문 URL 추출
   - 제목, 본문 핵심 문단, 발행일시, 출처 수집
   - 중복 체크 (URL 기반)
   ```

3. **데이터 정제**
   - HTML 태그 제거
   - 불필요한 광고/관련기사 제거
   - 텍스트 정규화

4. **DB 저장**
   - `news_article` 테이블에 저장
   - 컬럼: id, title, url, content_summary, source, published_at, created_at

5. **스케줄러 설정**
   - APScheduler로 매시간 또는 30분마다 자동 크롤링

#### 완료 기준
- [x] 뉴스가 DB에 정상 저장됨
- [x] 원문 URL이 모든 뉴스에 포함됨
- [x] 중복 뉴스가 저장되지 않음
- [x] 크롤링 에러 발생 시 로그 기록됨

#### 나중에 추가 작업
- [ ] 신문사(RSS 소스) 추가 (예: 서울경제, 이데일리 등)
- [ ] 소스별 ON/OFF 선택 기능 추가

#### 확인 사항
1. **robots.txt 준수 확인**
   - 각 뉴스사 사이트의 robots.txt 확인
   - 크롤링 간격 조절 (최소 1초 이상)

2. **저작권 준수**
   - 본문 전체 저장 금지
   - 제목 + 핵심 문단만 저장
   - 원문 링크 필수 포함

3. **DB 저장 테스트**
   ```sql
   SELECT * FROM news_article 
   ORDER BY published_at DESC 
   LIMIT 10;
   ```
   - URL 중복 확인
   - published_at 시간 정확성 확인

#### 주의 사항
- ⚠️ 과도한 크롤링으로 IP 차단되지 않도록 요청 간격 조절
- ⚠️ 본문 전체 저장 금지 (저작권 위반)
- ⚠️ 에러 발생 시 크롤링 중단되지 않도록 예외 처리

#### 개발 변경 예정
1. **소스별 수집 상태 가시화 강화**
   - 소스별 RSS 진입 건수, robots 차단 건수, 본문 수집 성공 건수, DB 저장 건수 로그 추가
   - 실행 종료 시 소스별 요약 로그를 1줄로 출력하여 운영 점검 시간 단축

2. **robots 차단 대응 정책 명확화**
   - robots 차단 시 본문 요청은 중단하고, RSS의 제목/요약/링크 중심으로 fallback 저장
   - 특정 소스 차단률 급증 시 알림(로그 기준 임계치)으로 운영자가 빠르게 인지 가능하도록 개선

3. **소스별 ON/OFF 운영 기능 우선 적용**
   - 환경변수 기반으로 소스별 활성화/비활성화 제어
   - 장애/차단 소스는 즉시 OFF, 대체 소스 ON 방식으로 운영 유연성 확보

4. **검증 지표 표준화**
   - daily 기준 `rss_items`, `robots_blocked`, `inserted` 저장/집계 기준 수립
   - `robots_block_rate`, `insert_rate`를 기준으로 품질 저하 여부 판단

#### 구현 방식 (예정)
- `src/rss_sources.py`에서 소스 정의를 유지하되, 소스별 활성화 설정값을 함께 참조하도록 확장
- `src/crawler.py`의 `collect_articles()`에 소스별 카운터를 추가하고 실행 마지막에 요약 로그 출력
- robots 차단/본문 수집 실패/요약 fallback 경로를 구분해 로그 레벨과 메시지 형식을 통일
- 필요 시 별도 집계 테이블(예: `crawl_run_metric`) 또는 일별 리포트 쿼리로 운영 지표를 저장
- 운영 단계에서는 차단률 임계치(예: 80% 이상) 초과 시 알림 전송을 연결

#### 변경 후 확인 항목 (운영 체크리스트)
1. **로그 확인 (1회 실행 기준)**
   - 실행: `python -m src.main --job news --once`
   - 소스별 `크롤링 완료 source=... collected=... inserted=...` 로그가 모두 출력되는지 확인
   - `robots.txt 차단으로 스킵`이 특정 소스에 과도하게 몰리는지 확인
   - 판정 예시:
     - 연합뉴스만 `inserted > 0`, 나머지 `inserted = 0`이면 소스별 차단/중복/피드 상태 점검 필요
     - 모든 소스 `inserted = 0`이면 DB 연결/중복 데이터 누적/요약 추출 실패 여부 우선 점검

2. **DB 결과 확인 (소스별 건수)**
   ```sql
   SELECT source, COUNT(*) AS cnt
   FROM news_article
   WHERE created_at >= NOW() - INTERVAL '1 day'
   GROUP BY source
   ORDER BY cnt DESC;
   ```
   - 특정 소스가 0건이면 해당 소스 로그에서 robots 차단/본문 실패 메시지 동반 여부 확인

3. **중복 저장 여부 확인**
   ```sql
   SELECT url, COUNT(*) AS cnt
   FROM news_article
   GROUP BY url
   HAVING COUNT(*) > 1;
   ```
   - 결과가 0건이면 URL 중복 방지는 정상 동작으로 판단

4. **발행시각/최신성 확인**
   ```sql
   SELECT source, title, published_at, created_at
   FROM news_article
   ORDER BY created_at DESC
   LIMIT 30;
   ```
   - `published_at`이 비정상적으로 비어 있거나 오래된 기사만 반복 저장되는지 확인

5. **운영 판정 기준 (권장)**
   - `robots_block_rate`가 80% 이상인 소스가 2회 연속 발생하면 경고
   - `inserted = 0`이 2회 연속 발생한 소스는 임시 OFF 후 대체 소스로 보완
   - 배치 자체 실패(예외 종료)는 즉시 점검 대상으로 분류


---

### **STEP 1-2: Python 주가 수집기 구현**
**예상 기간**: 1주

#### 개발 목표
- FinanceDataReader를 이용한 주가 데이터 수집
- 등락률, 거래량, 52주 고점 대비 계산
- PostgreSQL DB 저장

#### 구체적 구현 내용
1. **주가 데이터 수집**
   - FinanceDataReader 설치 및 설정
   - 종목별 일별 주가 데이터 수집 (시가, 고가, 저가, 종가, 거래량)

2. **지표 계산**
   - 전일 대비 등락률 (1일)
   - 5일 등락률
   - 1개월 등락률
   - 52주 고점 대비 하락률 (Drawdown)
   - 거래량 평균 대비 배율

3. **데이터 저장**
   - `stock_price_snapshot` 테이블에 저장
   - 컬럼: stock_id, base_date, close_price, change_rate_1d, change_rate_5d, change_rate_1m, volume_change_rate, drawdown_52w

4. **스케줄러 설정**
   - 평일 오전 8시 30분 자동 실행 (장 시작 전)

#### 완료 기준
- [x] 주가 데이터가 DB에 정상 저장됨
- [x] 등락률 계산이 정확함
- [x] 거래량 배율 계산이 정확함
- [x] 52주 고점 대비 계산이 정확함

#### 나중에 추가 작업
- [ ] 배치 스케줄러 작업 확인

#### 확인 사항
1. **데이터 정확성 검증**
   ```python
   # 네이버 증권과 비교하여 검증
   - 삼성전자 종가 비교
   - 등락률 비교
   - 거래량 비교
   ```

2. **DB 저장 테스트**
   ```sql
   SELECT * FROM stock_price_snapshot 
   WHERE stock_id = (SELECT id FROM stock WHERE ticker = '005930')
   ORDER BY base_date DESC 
   LIMIT 5;
   ```

3. **예외 상황 처리**
   - 장 휴장일 처리
   - 거래 정지 종목 처리
   - 데이터 누락 시 재시도

#### 주의 사항
- ⚠️ FinanceDataReader API 제한 확인
- ⚠️ 주말/공휴일에는 실행 안 되도록 설정
- ⚠️ 52주 데이터 없는 신규 상장 종목 예외 처리

#### 개발 변경 예정
1. **지표 명칭 정합화**
   - `change_rate_1m`를 `change_rate_21d`로 변경하여 계산 로직(21거래일)과 컬럼명을 일치
   - SQL/모델/저장 쿼리/조회 문서의 용어를 동일하게 맞춰 혼동 제거

2. **예외 상황 처리 가시화 강화**
   - 휴장일/데이터 부족/종목별 실패를 구분해 로그에 명확히 기록
   - 배치 결과에 `failed`와 `snapshots`를 함께 남겨 부분 실패 여부를 즉시 판단 가능하도록 개선

3. **스케줄러 운영 점검 항목 고정화**
   - 평일 08:30 트리거 동작 확인 절차 표준화
   - 중복 실행 방지(`max_instances=1`)와 동일 날짜 upsert 갱신 검증 절차 문서화

4. **종목 마스터 운영 기준 정리**
   - `stock.ticker` 입력 규칙(국내/미국 코드 체계)과 `market` 값 표준 정의
   - 추적 대상 종목(기사 관련 우선)부터 단계적으로 확장하는 운영 방식 명시

#### 구현 방식 (예정)
- `python-crawler/sql/002_create_stock_price_snapshot.sql`에 컬럼 rename migration을 추가
- `src/models.py`, `src/db.py`, 조회 SQL 예시를 `change_rate_21d` 기준으로 맞춤
- `src/stock_crawler.py`는 기존 21거래일 계산(`shift(21)`)을 유지하고 필드명만 정합화
- 주가 배치 실행 결과 로그에 성공/실패/저장 건수를 유지하여 부분 실패 추적성 확보
- 스케줄러 점검은 `--once`(기능 검증) + 스케줄 실행(트리거 검증) 2단계로 분리 운영

#### 변경 후 확인 항목 (운영 체크리스트)
1. **지표 컬럼 확인**
   ```sql
   SELECT column_name
   FROM information_schema.columns
   WHERE table_name = 'stock_price_snapshot'
   ORDER BY ordinal_position;
   ```
   - `change_rate_21d`가 존재하고 `change_rate_1m`가 제거(또는 사용 중지)되었는지 확인

2. **데이터 적재 및 중복 확인**
   ```sql
   SELECT stock_id, base_date, COUNT(*) AS cnt
   FROM stock_price_snapshot
   GROUP BY stock_id, base_date
   HAVING COUNT(*) > 1;
   ```
   - 결과 0건이면 upsert가 정상 동작 중으로 판단

3. **실행 결과 로그 확인**
   - 실행: `python -m src.main --job stock --once`
   - `주가 수집 완료 stocks=... snapshots=... affected=... failed=...` 로그 확인
   - `failed > 0`이어도 전체 배치가 종료되지 않고 완료 로그가 출력되면 부분 실패 처리는 정상

4. **휴장일/데이터 부족 검증**
   ```sql
   SELECT s.ticker, p.base_date, p.close_price, p.drawdown_52w
   FROM stock_price_snapshot p
   JOIN stock s ON s.id = p.stock_id
   ORDER BY p.base_date DESC, s.ticker
   LIMIT 30;
   ```
   - 휴장일 실행 시 최신 거래일 기준으로 저장되는지 확인
   - 신규상장/데이터 부족 종목에서 `drawdown_52w`가 NULL로 저장되는지 확인

5. **스케줄러 동작 점검**
   - 환경값: `STOCK_SCHEDULE_HOUR=8`, `STOCK_SCHEDULE_MINUTE=30`
   - 스케줄 실행: `python -m src.main --job stock`
   - 평일(mon-fri) 08:30 트리거와 중복 실행 방지(`max_instances=1`) 로그 확인

---

### **STEP 1-3: Java 기본 구조 세팅**
**예상 기간**: 1주

#### 개발 목표
- Spring Boot 프로젝트 기본 구조 구축
- PostgreSQL 연동
- JPA Entity 전체 테이블 설계

#### 구체적 구현 내용
1. **프로젝트 초기 설정**
   - Spring Boot 3.x 프로젝트 생성
   - Gradle 의존성 설정
   ```gradle
   dependencies {
       implementation 'org.springframework.boot:spring-boot-starter-web'
       implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
       implementation 'org.postgresql:postgresql'
       implementation 'org.springframework.boot:spring-boot-starter-validation'
       implementation 'org.projectlombok:lombok'
       // LangChain4j는 STEP 1-7에서 추가
   }
   ```

2. **패키지 구조 설계**
   ```
   src/main/java/com/marketlens/
   ├── domain/
   │   ├── news/
   │   │   ├── entity/
   │   │   ├── repository/
   │   │   └── service/
   │   ├── stock/
   │   │   ├── entity/
   │   │   ├── repository/
   │   │   └── service/
   │   ├── analysis/
   │   │   ├── entity/
   │   │   ├── repository/
   │   │   └── service/
   │   └── tracking/
   │       ├── entity/
   │       ├── repository/
   │       └── service/
   ├── telegram/
   │   ├── bot/
   │   └── service/
   ├── scheduler/
   └── config/
   ```

3. **Entity 설계 및 생성**
   
   **Phase 1 필수 테이블**:
   - `stock`: 종목 기본 정보
   - `news_article`: 뉴스 기사
   - `article_stock_mapping`: 기사-종목 매핑
   - `stock_price_snapshot`: 주가 스냅샷
   - `agent_analysis`: AI 분석 결과
   - `price_tracking`: 주가 반응 추적
   - `hot_stock_report`: 핫 종목 리포트
   - `agent_execution_log`: Agent 실행 로그
   - `telegram_send_log`: 텔레그램 발송 로그

   **Phase 2를 위한 테이블 (구조만 생성)**:
   - `users`: 사용자 정보
   - `user_stock`: 사용자-종목 관심 목록

4. **DB 연동 설정**
   ```yaml
   # application.yml
   spring:
     datasource:
       url: jdbc:postgresql://localhost:5432/marketlens
       username: ${DB_USERNAME}
       password: ${DB_PASSWORD}
     jpa:
       hibernate:
         ddl-auto: validate  # 운영에서는 validate, 개발에서는 update
       show-sql: true
   ```

5. **환경 변수 관리**
   - `.env` 파일 생성 (Git 제외)
   - 환경 변수: DB_USERNAME, DB_PASSWORD, TELEGRAM_BOT_TOKEN, OPENAI_API_KEY

#### 완료 기준
- [ ] Spring Boot 애플리케이션이 정상 실행됨
- [ ] PostgreSQL 연결 성공
- [ ] 모든 Entity가 테이블로 생성됨
- [ ] JPA Repository 테스트 성공

#### 확인 사항
1. **DB 연결 테스트**
   ```java
   @SpringBootTest
   class DatabaseConnectionTest {
       @Autowired
       private DataSource dataSource;
       
       @Test
       void testConnection() throws SQLException {
           assertNotNull(dataSource.getConnection());
       }
   }
   ```

2. **테이블 생성 확인**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

3. **Entity-Table 매핑 확인**
   - 각 Entity에 대한 CRUD 테스트 작성

#### 주의 사항
- ⚠️ API 키는 절대 코드에 하드코딩하지 않기
- ⚠️ `.env` 파일은 `.gitignore`에 추가
- ⚠️ `ddl-auto: create`는 개발 초기에만 사용, 이후 `validate`로 변경

---

### **STEP 1-4: Java B 기능 - 관심 종목 AI 분석 + 패턴 감지 + 발송**
**예상 기간**: 1주

#### 개발 목표
- OpenAI API 연동
- 관심 종목 분석 파이프라인 구현
- 패턴 감지 결과 포함 리포트 생성
- 텔레그램 전문 발송
- DB 저장 (Phase 2 대비)

#### 구체적 구현 내용
1. **OpenAI API 연동**
   ```java
   dependencies {
       implementation 'com.theokanning.openai-gpt3-java:service:0.18.2'
   }
   ```
   - API 키 설정
   - gpt-4o-mini (필터링용), gpt-4o (분석용) 분리

2. **분석 파이프라인 구현**
   ```
   1) DB에서 관심 종목 조회 (Phase 1에서는 하드코딩 또는 직접 DB 입력)
   2) Python 수집 데이터 조회 (뉴스, 주가)
   3) AI 프롬프트 생성
   4) OpenAI API 호출 및 분석
   5) 패턴 감지 로직 적용
   6) 리포트 생성
   7) DB 저장
   8) 텔레그램 발송
   ```

3. **AI 프롬프트 설계**
   ```
   역할: 주식 리서치 애널리스트
   
   입력 데이터:
   - 종목명, 티커
   - 최근 뉴스 (제목, 요약, URL, 발행일)
   - 주가 데이터 (전일/5일/1개월 등락률, 거래량 배율, 52주 대비)
   
   분석 요청:
   1. 뉴스 패턴 감지 (긍정/부정/중립 신호 강도)
   2. 단기 모멘텀 판단 (상승/하락/중립 가능성)
   3. 거래량 이상 여부
   4. 주가 선반영 여부
   5. 긍정 요인, 부정 요인, 리스크, 확인 포인트
   
   출력 형식: JSON
   ```

4. **패턴 감지 로직**
   - 뉴스 긍정/부정 비율 계산
   - 거래량 평균 대비 배율 계산
   - 단기 주가 급등락 감지
   - 패턴 신호 강도 레벨링 (강함/보통/약함)

5. **리포트 생성**
   - 텔레그램 메시지 포맷 구성
   - 원문 링크 포함
   - 패턴 감지 결과 이모지로 표현
   - 면책 문구 필수 포함

6. **텔레그램 발송**
   - Telegram Bot API 연동
   - 메시지 포맷팅 (Markdown 또는 HTML)
   - 에러 처리 및 재시도

7. **DB 저장**
   - `agent_analysis` 테이블에 분석 결과 저장
   - Phase 2 웹 UI에서 조회 가능하도록 구조화

#### 완료 기준
- [ ] OpenAI API 호출 성공
- [ ] 패턴 감지 결과가 리포트에 포함됨
- [ ] 원문 링크가 모두 포함됨
- [ ] 텔레그램으로 리포트 수신됨
- [ ] DB에 분석 결과 저장 확인

#### 확인 사항
1. **AI 응답 품질 검증**
   - 삼성전자, SK하이닉스 등 대표 종목으로 테스트
   - 분석 내용이 실제 뉴스와 일치하는지 확인
   - 패턴 감지 결과가 합리적인지 검증

2. **텔레그램 메시지 확인**
   ```
   - 메시지가 너무 길어서 잘리지 않는지
   - 링크 클릭 시 정상 이동하는지
   - 이모지가 제대로 표시되는지
   - 면책 문구가 포함되어 있는지
   ```

3. **DB 저장 확인**
   ```sql
   SELECT * FROM agent_analysis 
   ORDER BY analysis_date DESC 
   LIMIT 5;
   ```

4. **비용 모니터링**
   - OpenAI API 사용량 확인
   - 종목 1개당 예상 비용 계산

#### 주의 사항
- ⚠️ OpenAI API 타임아웃 설정 (30초)
- ⚠️ 텔레그램 메시지 길이 제한 (4096자)
- ⚠️ API 키 노출 방지
- ⚠️ 면책 문구 필수 포함

---

### **STEP 1-5: Java 주가 반응 추적 스케줄러**
**예상 기간**: 1주

#### 개발 목표
- 분석 시점 주가 저장
- 3일/1주 후 실제 주가 자동 추적
- 패턴 적중률 DB 저장

#### 구체적 구현 내용
1. **분석 시점 주가 저장**
   - `agent_analysis` 저장 시 당시 주가도 함께 저장
   - `price_tracking` 테이블에 추적 대상 등록

2. **추적 스케줄러 구현**
   ```java
   @Scheduled(cron = "0 0 16 * * MON-FRI")  // 평일 오후 4시
   public void trackPriceReactions() {
       // 3일 후 추적 대상 조회 및 주가 수집
       // 1주 후 추적 대상 조회 및 주가 수집
   }
   ```

3. **거래일 계산 로직**
   - 주말/공휴일 제외한 실제 거래일 계산
   - 3거래일 후, 5거래일 후 정확히 계산

4. **패턴 적중 여부 판단**
   ```
   - 긍정 패턴 감지 → 실제 상승 (3% 이상) → 적중
   - 긍정 패턴 감지 → 실제 하락 → 불일치
   - 부정 패턴 감지 → 실제 하락 → 적중
   - 부정 패턴 감지 → 실제 상승 → 불일치
   ```

5. **적중률 통계 계산**
   - 전체 분석 건수
   - 패턴 적중 건수
   - 패턴별 적중률 (긍정 패턴, 부정 패턴)

6. **DB 저장**
   - `price_tracking` 테이블에 결과 저장
   - `pattern_matched` 필드에 true/false 저장

#### 완료 기준
- [ ] 3일 후 주가가 자동으로 DB에 저장됨
- [ ] 1주 후 주가가 자동으로 DB에 저장됨
- [ ] 패턴 적중 여부가 정확히 판단됨
- [ ] 적중률 통계 조회 가능

#### 확인 사항
1. **스케줄러 동작 확인**
   ```java
   // 로그 확인
   [INFO] Price tracking scheduler started
   [INFO] Tracked 5 stocks for 3-day analysis
   [INFO] Tracked 3 stocks for 1-week analysis
   ```

2. **거래일 계산 검증**
   - 금요일 분석 → 다음주 수요일 추적 (3거래일)
   - 금요일 분석 → 다음주 금요일 추적 (5거래일)

3. **DB 확인**
   ```sql
   SELECT * FROM price_tracking 
   WHERE price_3d_later IS NOT NULL
   ORDER BY tracked_at DESC;
   ```

4. **적중률 확인**
   ```sql
   SELECT 
       COUNT(*) as total,
       SUM(CASE WHEN pattern_matched THEN 1 ELSE 0 END) as matched,
       ROUND(SUM(CASE WHEN pattern_matched THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy
   FROM price_tracking
   WHERE price_3d_later IS NOT NULL;
   ```

#### 주의 사항
- ⚠️ 공휴일 처리 (한국 거래소 휴장일 캘린더 필요)
- ⚠️ 거래 정지 종목 처리
- ⚠️ 상한가/하한가 종목 처리

---

### **STEP 1-6: Java 텔레그램 커맨드 처리**
**예상 기간**: 1주

#### 개발 목표
- Telegram Bot 커맨드 핸들러 구현
- 사용자 명령 처리 및 응답

#### 구체적 구현 내용
1. **텔레그램 Bot 초기 설정**
   - BotFather에서 Bot 생성
   - Token 발급 및 환경 변수 설정
   - Webhook 또는 Long Polling 설정

2. **커맨드 구현**
   
   **/add [종목코드] [종목명]**
   ```
   - Phase 1: DB에 직접 종목 추가 (user_id는 고정값 또는 NULL)
   - 중복 체크
   - 종목 코드 유효성 검증
   - 응답: "✅ [종목명]이 관심 종목에 추가되었습니다."
   ```

   **/remove [종목코드]**
   ```
   - DB에서 종목 삭제
   - 응답: "✅ [종목명]이 관심 종목에서 삭제되었습니다."
   ```

   **/list**
   ```
   - 현재 등록된 관심 종목 목록 조회
   - 응답: 
     📋 관심 종목 목록 (총 3개)
     1. 삼성전자 (005930)
     2. SK하이닉스 (000660)
     3. NAVER (035420)
   ```

   **/report [종목코드]**
   ```
   - 특정 종목의 최신 분석 리포트 조회
   - DB에서 최근 분석 결과 조회하여 발송
   ```

   **/today**
   ```
   - 오늘의 핫 종목 TOP 3 조회
   - DB에서 최신 hot_stock_report 조회하여 발송
   ```

   **/help**
   ```
   - 사용 가능한 커맨드 목록 안내
   ```

3. **에러 처리**
   - 잘못된 종목 코드 입력 시
   - 존재하지 않는 종목 삭제 시도 시
   - DB 에러 시

4. **응답 메시지 포맷팅**
   - Markdown 또는 HTML 모드
   - 버튼 추가 (InlineKeyboardButton - Phase 2 준비)

#### 완료 기준
- [ ] 모든 커맨드가 정상 동작함
- [ ] 에러 발생 시 적절한 안내 메시지 표시
- [ ] 커맨드 응답 속도 2초 이내

#### 확인 사항
1. **커맨드 테스트**
   ```
   /add 005930 삼성전자  → 성공
   /add 005930 삼성전자  → 중복 체크 메시지
   /add 999999 잘못된종목 → 에러 메시지
   /list                 → 종목 목록 표시
   /remove 005930        → 삭제 성공
   /list                 → 빈 목록
   /report 005930        → 최신 리포트 표시
   /today                → 핫 종목 TOP 3 표시
   /help                 → 도움말 표시
   ```

2. **DB 변경 확인**
   ```sql
   -- 커맨드 실행 후 DB 확인
   SELECT * FROM user_stock;  -- Phase 2 테이블이지만 구조 확인
   ```

3. **응답 시간 측정**
   - 커맨드 입력부터 응답까지 시간 로깅

#### 주의 사항
- ⚠️ Phase 1에서는 단일 사용자이므로 user_id 구분 불필요
- ⚠️ 텔레그램 메시지 길이 제한 (4096자)
- ⚠️ 동시에 여러 커맨드 입력 시 처리 순서

---

### **STEP 1-7: Java A 기능 - AI Agent 구현 (핫 종목 발굴)**
**예상 기간**: 2주

#### 개발 목표
- LangChain4j ReAct 루프 구현
- AI Agent가 자율적으로 툴 선택 및 실행
- 오늘의 핫 종목 TOP 3 발굴 및 패턴 감지
- 전문 텔레그램 발송 + DB 저장

#### 구체적 구현 내용
1. **LangChain4j 의존성 추가**
   ```gradle
   dependencies {
       implementation 'dev.langchain4j:langchain4j:0.27.1'
       implementation 'dev.langchain4j:langchain4j-open-ai:0.27.1'
   }
   ```

2. **AI Agent Tools 구현**
   
   **Tool 1: 경제 뉴스 수집 툴**
   ```java
   @Tool("오늘의 경제 뉴스를 수집합니다")
   public String collectTodayNews() {
       // DB에서 오늘 수집된 뉴스 조회
       // 종목별로 그룹핑
       // JSON 형태로 반환
   }
   ```

   **Tool 2: 주가 데이터 조회 툴**
   ```java
   @Tool("특정 종목의 주가 데이터를 조회합니다")
   public String getStockPrice(@P("종목코드") String ticker) {
       // DB에서 최신 주가 스냅샷 조회
       // 등락률, 거래량 배율 포함
       // JSON 형태로 반환
   }
   ```

   **Tool 3: 공시 정보 조회 툴** (선택적)
   ```java
   @Tool("특정 종목의 최근 공시를 조회합니다")
   public String getDisclosure(@P("종목코드") String ticker) {
       // OpenDART API 호출
       // 최근 1주일 주요 공시 조회
   }
   ```

   **Tool 4: 종목 상세 정보 조회 툴**
   ```java
   @Tool("특정 종목의 상세 정보를 조회합니다")
   public String getStockDetail(@P("종목코드") String ticker) {
       // 종목명, 시장, 섹터 정보 조회
   }
   ```

3. **ReAct Agent 구성**
   ```java
   @Service
   public class HotStockAgentService {
       
       private final AiServices aiService;
       
       public HotStockReport findHotStocks() {
           String systemPrompt = """
               당신은 주식 리서치 애널리스트입니다.
               오늘의 경제 뉴스를 분석하여 주목할 만한 종목 TOP 3을 발굴하세요.
               
               단계:
               1. 경제 뉴스 수집 툴을 호출하여 오늘의 뉴스를 확인하세요.
               2. 뉴스에서 자주 언급되는 종목들을 파악하세요.
               3. 주목할 종목 후보가 있다면 주가 데이터 툴로 추가 확인하세요.
               4. 뉴스 패턴과 주가 흐름을 종합하여 TOP 3 종목을 선정하세요.
               5. 각 종목별로 선정 이유, 패턴 감지 결과, 참고 기사를 정리하세요.
               
               패턴 감지 기준:
               - 긍정 신호: 긍정 뉴스가 부정 뉴스보다 3배 이상 많음
               - 단기 모멘텀: 거래량 평소 2배 이상 + 뉴스 급증
               - 주가 선반영: 최근 5일 등락률 10% 이상
               """;
           
           return aiService.generate(systemPrompt);
       }
   }
   ```

4. **Agent 동작 플로우**
   ```
   1. 스케줄러가 평일 오전 9시 Agent 실행
   2. Agent가 경제 뉴스 툴 호출 (자율 결정)
   3. 뉴스 분석하여 종목 후보 선정
   4. 종목 후보에 대해 주가 툴 호출 (자율 결정)
   5. 필요시 공시 툴 추가 호출 (자율 결정)
   6. 종합 판단하여 TOP 3 선정
   7. 리포트 생성 (선정 이유, 패턴, 참고 기사)
   8. DB 저장 (hot_stock_report 테이블)
   9. 텔레그램 발송
   ```

5. **리포트 생성 및 저장**
   - 각 종목별 선정 이유
   - 주가 수치 (전일, 5일 등락률, 거래량 배율)
   - 패턴 감지 결과 (긍정/부정 신호, 단기 모멘텀)
   - 참고 기사 링크 (최소 2개 이상)
   - 확인 포인트

6. **텔레그램 발송**
   - 헤더: "📊 오늘의 주목 종목 TOP 3"
   - 1위, 2위, 3위 종목 상세 정보
   - 원문 링크 포함
   - 면책 문구

#### 완료 기준
- [ ] AI Agent가 스스로 툴을 선택하여 호출함
- [ ] TOP 3 종목이 합리적으로 선정됨
- [ ] 패턴 감지 결과가 포함됨
- [ ] 참고 기사 링크가 포함됨
- [ ] DB에 저장됨
- [ ] 텔레그램으로 발송됨

#### 확인 사항
1. **Agent 동작 로그 확인**
   ```
   [Agent] Step 1: Calling tool 'collectTodayNews'
   [Agent] Step 2: Analyzing news... Found 15 news items
   [Agent] Step 3: Calling tool 'getStockPrice' for ticker '000660'
   [Agent] Step 4: Calling tool 'getStockPrice' for ticker '005930'
   [Agent] Step 5: Final decision - TOP 3: SK하이닉스, 삼성전자, 현대차
   ```

2. **툴 호출 순서 검증**
   - Agent가 뉴스 툴을 먼저 호출하는지
   - 필요에 따라 주가 툴을 추가로 호출하는지
   - 불필요한 툴 호출은 하지 않는지

3. **리포트 품질 검증**
   - 선정 이유가 뉴스와 일치하는지
   - 패턴 감지가 정확한지
   - 참고 기사가 실제로 관련성이 있는지

4. **DB 저장 확인**
   ```sql
   SELECT * FROM hot_stock_report 
   WHERE report_date = CURRENT_DATE 
   ORDER BY rank;
   ```

5. **비용 측정**
   - Agent 1회 실행당 OpenAI API 사용량
   - 예상 월 비용 계산

#### 주의 사항
- ⚠️ Agent가 무한 루프에 빠지지 않도록 최대 반복 횟수 설정 (예: 10회)
- ⚠️ 툴 호출 실패 시 에러 처리
- ⚠️ OpenAI API 타임아웃 길게 설정 (60초)
- ⚠️ Agent 실행 시간이 너무 길어지지 않도록 모니터링

---

### **STEP 1-8: 실행 로그 + 실패 처리**
**예상 기간**: 1주

#### 개발 목표
- Agent 및 스케줄러 실행 로그 저장
- 실패 시 재시도 로직 구현
- 에러 알림 발송

#### 구체적 구현 내용
1. **Agent 실행 로그 저장**
   - `agent_execution_log` 테이블에 저장
   - 컬럼: job_name, status, started_at, ended_at, error_message, retry_count

2. **텔레그램 발송 로그 저장**
   - `telegram_send_log` 테이블에 저장
   - 컬럼: user_id, execution_id, status, sent_at, error_message

3. **재시도 로직 구현**
   ```java
   @Retryable(
       value = {Exception.class},
       maxAttempts = 3,
       backoff = @Backoff(delay = 2000)
   )
   public void executeAgent() {
       // Agent 실행 로직
   }
   ```

4. **실패 처리**
   - 재시도 3회 후에도 실패 시 에러 로그 저장
   - 관리자 텔레그램으로 에러 알림 발송
   - 에러 메시지에는 실패 원인 포함

5. **스케줄러 모니터링**
   ```java
   @Scheduled(cron = "0 0 9 * * MON-FRI")
   public void scheduledHotStockAgent() {
       AgentExecutionLog log = new AgentExecutionLog();
       log.setJobName("HOT_STOCK_AGENT");
       log.setStartedAt(LocalDateTime.now());
       
       try {
           hotStockAgentService.execute();
           log.setStatus("SUCCESS");
       } catch (Exception e) {
           log.setStatus("FAILED");
           log.setErrorMessage(e.getMessage());
           notifyError(e);
       } finally {
           log.setEndedAt(LocalDateTime.now());
           executionLogRepository.save(log);
       }
   }
   ```

6. **에러 알림 포맷**
   ```
   ⚠️ 시스템 에러 발생
   
   작업: HOT_STOCK_AGENT
   시간: 2026-06-06 09:15:32
   에러: OpenAI API Timeout
   재시도: 3/3 실패
   
   수동 확인이 필요합니다.
   ```

#### 완료 기준
- [ ] 모든 실행이 DB에 로그로 저장됨
- [ ] 실패 시 3회 재시도됨
- [ ] 재시도 후에도 실패 시 에러 알림 수신됨
- [ ] 로그를 통해 실패 원인 파악 가능

#### 확인 사항
1. **로그 조회**
   ```sql
   -- 최근 실행 로그
   SELECT * FROM agent_execution_log 
   ORDER BY started_at DESC 
   LIMIT 10;
   
   -- 실패 로그
   SELECT * FROM agent_execution_log 
   WHERE status = 'FAILED' 
   ORDER BY started_at DESC;
   
   -- 텔레그램 발송 실패 로그
   SELECT * FROM telegram_send_log 
   WHERE status = 'FAILED' 
   ORDER BY sent_at DESC;
   ```

2. **재시도 동작 확인**
   - 일부러 에러를 발생시켜 재시도 테스트
   - 재시도 간격이 올바른지 확인

3. **에러 알림 수신 확인**
   - 관리자 텔레그램에 에러 메시지 도착 여부

#### 주의 사항
- ⚠️ 로그가 너무 많이 쌓이지 않도록 주기적 삭제 (예: 3개월 이상 된 로그)
- ⚠️ 에러 알림이 너무 자주 발송되지 않도록 제한 (예: 같은 에러는 1시간에 1회만)

---

### **STEP 1-9: Oracle Cloud 배포**
**예상 기간**: 1주

#### 개발 목표
- Docker Compose로 기존 서비스와 분리 배포
- GitHub Actions CI/CD 구축
- Nginx HTTPS 설정

#### 구체적 구현 내용
1. **Dockerfile 작성**
   
   **Java Backend**
   ```dockerfile
   FROM eclipse-temurin:17-jdk-alpine
   WORKDIR /app
   COPY build/libs/*.jar app.jar
   ENTRYPOINT ["java", "-jar", "app.jar"]
   ```

   **Python Crawler**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["python", "scheduler.py"]
   ```

2. **docker-compose.yml 작성**
   ```yaml
   version: '3.8'
   
   services:
     postgres:
       image: postgres:15-alpine
       environment:
         POSTGRES_DB: marketlens
         POSTGRES_USER: ${DB_USERNAME}
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data
       ports:
         - "5432:5432"
     
     python-crawler:
       build: ./python-crawler
       environment:
         DB_HOST: postgres
         DB_PORT: 5432
         DB_NAME: marketlens
         DB_USERNAME: ${DB_USERNAME}
         DB_PASSWORD: ${DB_PASSWORD}
       depends_on:
         - postgres
     
     java-backend:
       build: ./java-backend
       environment:
         SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/marketlens
         SPRING_DATASOURCE_USERNAME: ${DB_USERNAME}
         SPRING_DATASOURCE_PASSWORD: ${DB_PASSWORD}
         OPENAI_API_KEY: ${OPENAI_API_KEY}
         TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
       ports:
         - "8080:8080"
       depends_on:
         - postgres
   
   volumes:
     postgres_data:
   ```

3. **GitHub Actions 워크플로우**
   ```yaml
   # .github/workflows/deploy.yml
   name: Deploy to Oracle Cloud
   
   on:
     push:
       branches: [ main ]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up JDK 17
           uses: actions/setup-java@v3
           with:
             java-version: '17'
             distribution: 'temurin'
         
         - name: Build with Gradle
           run: ./gradlew build
         
         - name: Deploy to Oracle Cloud
           uses: appleboy/ssh-action@v0.1.10
           with:
             host: ${{ secrets.ORACLE_HOST }}
             username: ${{ secrets.ORACLE_USER }}
             key: ${{ secrets.ORACLE_SSH_KEY }}
             script: |
               cd /opt/marketlens
               git pull origin main
               docker-compose down
               docker-compose up -d --build
   ```

4. **Nginx 설정**
   ```nginx
   # /etc/nginx/sites-available/marketlens
   server {
       listen 80;
       server_name marketlens.yourdomain.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name marketlens.yourdomain.com;
       
       ssl_certificate /etc/letsencrypt/live/marketlens.yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/marketlens.yourdomain.com/privkey.pem;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Let's Encrypt SSL 인증서 발급**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d marketlens.yourdomain.com
   ```

6. **환경 변수 설정**
   - Oracle Cloud 서버에 `.env` 파일 생성
   - GitHub Secrets에 민감한 정보 저장

7. **DB 백업 스크립트**
   ```bash
   #!/bin/bash
   # backup.sh
   BACKUP_DIR="/opt/backups/marketlens"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   docker exec marketlens_postgres_1 pg_dump -U $DB_USERNAME marketlens > "$BACKUP_DIR/backup_$DATE.sql"
   
   # 7일 이상 된 백업 삭제
   find $BACKUP_DIR -type f -mtime +7 -delete
   ```

   ```bash
   # crontab 등록
   0 3 * * * /opt/marketlens/backup.sh
   ```

#### 완료 기준
- [ ] Docker Compose로 모든 서비스 정상 실행
- [ ] GitHub push 시 자동 배포됨
- [ ] HTTPS 접속 가능
- [ ] 매일 오전 9시 리포트 수신됨
- [ ] DB 백업이 매일 자동 실행됨

#### 확인 사항
1. **Docker 컨테이너 상태 확인**
   ```bash
   docker-compose ps
   docker-compose logs -f java-backend
   docker-compose logs -f python-crawler
   ```

2. **서비스 접근 확인**
   ```bash
   curl https://marketlens.yourdomain.com/actuator/health
   ```

3. **스케줄러 동작 확인**
   - 매일 오전 9시에 리포트가 정상 발송되는지 확인
   - 3일 연속 모니터링

4. **리소스 사용량 모니터링**
   ```bash
   docker stats
   df -h  # 디스크 사용량
   free -h  # 메모리 사용량
   ```

5. **백업 확인**
   ```bash
   ls -lh /opt/backups/marketlens/
   ```

#### 주의 사항
- ⚠️ 기존 서비스와 포트 충돌 주의
- ⚠️ Oracle Cloud 방화벽 규칙 설정 (8080 포트 허용)
- ⚠️ 환경 변수 노출 방지 (`.env` 파일 권한 600)
- ⚠️ 메모리 부족 시 컨테이너 재시작될 수 있음 (모니터링 필요)

---

## 📊 Phase 1 완료 체크리스트

### 기능 완성도
- [ ] 매일 오전 9시 오늘의 핫 종목 TOP 3 자동 발송
- [ ] 관심 종목 분석 리포트 자동 발송
- [ ] 텔레그램 커맨드로 종목 추가/삭제/조회 가능
- [ ] 패턴 감지 결과 포함
- [ ] 원문 링크 포함
- [ ] 3일/1주 후 주가 반응 추적
- [ ] 면책 문구 포함

### 데이터 품질
- [ ] 뉴스 중복 없이 수집됨
- [ ] 주가 데이터 정확함
- [ ] 원문 링크 클릭 시 정상 이동

### 안정성
- [ ] 3일 이상 에러 없이 연속 실행
- [ ] 실패 시 재시도 동작
- [ ] 에러 발생 시 알림 수신

### 배포
- [ ] Docker Compose로 실행 중
- [ ] GitHub push 시 자동 배포
- [ ] HTTPS 적용
- [ ] DB 백업 자동 실행

### 비용
- [ ] OpenAI API 월 사용량 3,000원 이내
- [ ] Oracle Cloud 무료 티어 범위 내

---

## 🎯 Phase 1 완료 후 다음 단계

### 포트폴리오 제출 준비
1. **README 작성**
   - 프로젝트 소개
   - 주요 기능 스크린샷
   - 기술 스택
   - 아키텍처 다이어그램
   - 실행 방법

2. **GitHub 정리**
   - 커밋 메시지 정리
   - 코드 주석 정리
   - 불필요한 파일 삭제

3. **데모 영상 제작**
   - 텔레그램 리포트 수신 화면
   - 커맨드 동작 시연
   - AI Agent 로그 확인

### Phase 2 준비
- 웹 UI 설계 시작
- React 프로젝트 구조 설계
- API 명세서 작성

---

## ⚠️ 전체 주의 사항

### 법적 / 윤리
- 투자 권유가 아닌 정보 제공임을 명확히
- 면책 문구 필수 포함
- 저작권 준수 (원문 링크만 제공)

### 보안
- API 키 절대 코드에 하드코딩 금지
- 환경 변수로 관리
- `.env` 파일 `.gitignore`에 추가

### 비용 관리
- OpenAI API 월 한도 설정 필수
- 사용량 주기적 모니터링

### 데이터 품질
- 뉴스 크롤링 시 robots.txt 준수
- 주가 데이터 정확성 검증
- 중복 데이터 제거

---

## 📞 문제 발생 시 체크 포인트

### 텔레그램 메시지가 안 옴
1. Bot Token 확인
2. Chat ID 확인
3. 텔레그램 발송 로그 확인
4. 네트워크 연결 확인

### AI 분석이 이상함
1. 프롬프트 재검토
2. 입력 데이터 확인 (뉴스, 주가)
3. OpenAI API 응답 로그 확인

### 뉴스 크롤링 실패
1. 뉴스 사이트 구조 변경 여부 확인
2. robots.txt 확인
3. IP 차단 여부 확인

### DB 연결 실패
1. PostgreSQL 컨테이너 상태 확인
2. 환경 변수 확인
3. 네트워크 연결 확인

### 배포 실패
1. Docker 컨테이너 로그 확인
2. GitHub Actions 로그 확인
3. 디스크 용량 확인

---

## 📈 성공 지표

### 기술적 지표
- 시스템 가동률 99% 이상
- 평균 응답 시간 2초 이내
- 일일 에러 발생 0건

### 품질 지표
- 뉴스 중복률 0%
- 주가 데이터 정확도 100%
- 패턴 감지 적중률 60% 이상

### 비용 지표
- 월 운영 비용 3,000원 이내
- OpenAI API 사용량 예산 내

---

**Phase 1 완료 시 포트폴리오 제출 가능!**
