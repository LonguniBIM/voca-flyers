#!/usr/bin/env python3
"""User-visible learning-flow checks in a disposable browser context."""
import argparse
import http.server
import json
import re
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--report', required=True)
parser.add_argument('--channel')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
checks = []


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split('?', 1)[0]
        if not path.startswith('/voca-flyers/'):
            return str(root / '__missing__')
        target = (root / path[len('/voca-flyers/'):]).resolve()
        return str(target) if target.is_relative_to(root) else str(root / '__missing__')

    def log_message(self, *unused):
        pass


def check(value, name):
    assert value, name
    checks.append(name)


def ready(page):
    page.wait_for_function("window.FlyersAppStatus && !document.getElementById('start').disabled")


def state(page):
    return page.evaluate("""async()=>{
        const store = await new FlyersStore().open();
        const data = {sessions: await store.list(), prefs: await store.meta('preferences', {})};
        store.db?.close();
        return data;
    }""")


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/voca-flyers/'

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel=args.channel)
        context = browser.new_context(service_workers='block')
        page = context.new_page()
        page.goto(url, wait_until='networkidle')
        ready(page)

        page.locator('#autolisten').uncheck()
        page.locator('#clearTopics').click()
        page.locator('#topicCards input').first.check()
        page.locator('#sessionSize').fill('1')
        page.evaluate("()=>{RiseG5Core.sample=(pool)=>pool.slice(0,1);}")
        page.locator('#start').click()
        page.wait_for_function("!document.getElementById('game').hidden")

        answer = state(page)['sessions'][0]['questions'][0]['answer']
        page.evaluate("""()=>{
            window.__spokenAnswers = [];
            speechSynthesis.cancel = ()=>{};
            speechSynthesis.getVoices = ()=>[];
            speechSynthesis.speak = utterance=>{
                window.__spokenAnswers.push(utterance.text);
                utterance.onstart?.();
                utterance.onend?.();
            };
        }""")
        page.locator('#questionTitle').click()
        page.keyboard.type(re.sub('[^A-Za-z]', '', answer))
        page.locator('#check').click()
        page.locator('#answerBox').wait_for(state='visible')
        check(page.evaluate('window.__spokenAnswers') == [answer], 'correct answer is automatically spoken once')

        page.locator('#next').click()
        page.wait_for_function("!document.getElementById('detail').hidden")
        page.locator('#detailNew').click()
        page.locator('#clearTopics').click()
        page.locator('#topicCards input').first.check()
        page.locator('#sessionSize').fill('2')
        page.evaluate("""()=>{
            RiseG5Core.sample=(pool,count)=>{
                const seen = new Set();
                const selected = [];
                for (const word of pool) {
                    const key = RiseG5Core.canonical(word.word);
                    if (!seen.has(key)) {
                        seen.add(key);
                        selected.push(word);
                    }
                    if (selected.length === count) break;
                }
                return selected;
            };
        }""")
        page.locator('#start').click()
        page.wait_for_function("!document.getElementById('game').hidden")
        active = next(session for session in state(page)['sessions'] if session['status'] == 'in_progress')
        skipped_answer = active['questions'][0]['answer']

        page.locator('#skip').click()
        page.wait_for_timeout(100)
        check(not page.locator('#answerBox').is_hidden(), 'skip reveals the answer without advancing')
        check(page.locator('#correctWord').inner_text() == skipped_answer, 'skip shows the exact answer')
        check(not page.locator('#next').is_hidden() and page.locator('#skip').is_hidden() and page.locator('#check').is_hidden(), 'skip waits for an explicit Next word action')
        active = next(session for session in state(page)['sessions'] if session['status'] == 'in_progress')
        check(active['index'] == 0 and active['questions'][0]['skippedAt'] and not active['questions'][0]['firstCorrect'], 'skip remains a skipped outcome, not a correct or wrong answer')

        page.locator('#pause').click()
        page.wait_for_function("!document.getElementById('home').hidden && !FlyersAppStatus().pending")
        page.reload(wait_until='networkidle')
        ready(page)
        page.locator('#resume').click()
        page.wait_for_function("!document.getElementById('game').hidden")
        check(page.locator('#questionNumber').inner_text() == 'Question 1 / 2' and not page.locator('#answerBox').is_hidden(), 'resuming a skipped word preserves the revealed answer')
        page.locator('#next').click()
        page.wait_for_function("document.getElementById('questionNumber').textContent === 'Question 2 / 2'")
        check(page.locator('#answerBox').is_hidden() and not page.locator('#skip').is_hidden(), 'Next word advances only after the learner chooses it')

        context.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()

report = {'passed': len(checks), 'checks': checks}
Path(args.report).write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
