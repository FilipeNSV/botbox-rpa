from playwright.sync_api import sync_playwright
from config import BASE_URL, USERNAME, PASSWORD
from datetime import datetime, timedelta

class BootboxBot:
    def __init__(self):
        # Inicializa o Playwright e abre o navegador em modo visível (não headless)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        # Cria um contexto sem viewport fixo (permite fullscreen real)
        self.context = self.browser.new_context(no_viewport=True)
        self.page = self.context.new_page()

        # Armazena o último título de tarefa criado
        self.last_task_title = None

    # -----------------------------
    # Autenticação
    # -----------------------------
    def open(self):
        # Acessa a aplicação e aguarda o campo de login
        self.page.goto(BASE_URL)
        self.page.wait_for_selector('input[placeholder="Email"]', timeout=60000)

    def login(self):
        # Preenche credenciais e realiza login
        self.page.fill('input[placeholder="Email"]', USERNAME)
        self.page.fill('input[placeholder="Senha"]', PASSWORD)
        self.page.click('button:has-text("Entrar")')

        # Aguarda carregamento básico da página
        self.page.wait_for_load_state("domcontentloaded")

        # Aguarda elemento que indica login bem-sucedido
        self.page.wait_for_selector('a.nav-link[href="/tarefas"]', timeout=60000)

    # -----------------------------
    # Navegação
    # -----------------------------
    def go_to_tasks(self):
        # Navega até a tela de tarefas
        self.page.click('a.nav-link[href="/tarefas"]')
        self.page.wait_for_load_state("domcontentloaded")

        # Aguarda botão de adicionar tarefa estar disponível
        self.page.wait_for_selector('button[data-target="#addTarefa"]', timeout=60000)

    # -----------------------------
    # Criação de Tarefa
    # -----------------------------
    def open_add_task_modal(self):
        # Abre o modal de criação de tarefa
        self.page.click('button[data-target="#addTarefa"]')
        self.page.wait_for_selector('#addTarefa', timeout=60000)

        modal = self.page.locator("#addTarefa")
        modal.wait_for(state="visible", timeout=60000)
        return modal

    def set_priority_in_add_modal(self, modal, priority="ALTA"):
        """
        Define a prioridade da tarefa no modal de criação.
        Tenta diferentes seletores possíveis com base no HTML.
        """
        candidates = [
            f'[title="{priority}"]',
            f'[title*="{priority}"]',
            f'text={priority}',
        ]

        for sel in candidates:
            loc = modal.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.click()
                    return
                except:
                    pass

    def create_task(self):
        # Gera título único baseado na data/hora atual
        now = datetime.now()
        title = f"RPA - {now.strftime('%d/%m/%Y %H:%M:%S')}"
        self.last_task_title = title

        modal = self.open_add_task_modal()

        # 1. Preenche título da tarefa
        modal.locator("input#nome").wait_for(state="visible", timeout=60000)
        modal.locator("input#nome").fill(title)

        # 2. Seleciona fluxo (Desenvolvimento)
        fluxo = modal.locator("select#fluxo_id")
        fluxo.wait_for(state="visible", timeout=60000)
        fluxo.select_option(value="4")

        # 3. Seleciona projeto via componente Chosen
        projeto_chosen = modal.locator("#projeto_id_chosen")
        projeto_chosen.wait_for(state="visible", timeout=60000)

        projeto_chosen.locator("a.chosen-single").click()

        search_input = projeto_chosen.locator(".chosen-search input")
        search_input.wait_for(state="visible", timeout=60000)
        search_input.fill("Agily - Agily Tecnologia")

        projeto_chosen.locator(
            ".chosen-results li.active-result",
            has_text="Agily - Agily Tecnologia"
        ).first.click()

        # 4. Define datas e horários
        start_date = now.strftime("%d/%m/%Y")
        end_date = (now + timedelta(days=1)).strftime("%d/%m/%Y")

        modal.locator("input#data_inicio").fill(start_date)

        hora_inicio = modal.locator("select#hora_inicio").first
        hora_inicio.wait_for(state="visible")
        hora_inicio.select_option(value="20:00:00")

        modal.locator("input#data_fim").fill(end_date)

        hora_fim = modal.locator("select#hora_fim").first
        hora_fim.wait_for(state="visible")
        hora_fim.select_option(value="20:30:00")

        # 5. Define prioridade
        self.set_priority_in_add_modal(modal, priority="ALTA")

        # 6. Define estimativa
        modal.locator("input#estimativa").fill("2430")

        # 7. Preenche detalhes (editor Summernote ou textarea fallback)
        if modal.locator('a[href="#detalhes"], a#detalhes-tab').count() > 0:
            modal.locator('a[href="#detalhes"], a#detalhes-tab').first.click()

        editor = modal.locator(".note-editable[contenteditable='true']").first

        if editor.count() > 0:
            editor.click()
            editor.fill("Esta é uma tarefa de teste para aprendizado de RPA. Bom, lá vai… Hello World! :)")
        else:
            ta = modal.locator("textarea").first
            if ta.count() > 0:
                ta.fill("Esta é uma tarefa de teste para aprendizado de RPA. Bom, lá vai… Hello World! :)")

        # 8. Adiciona comentário inicial
        self.page.locator("a#comentarios-tab").click()

        self.page.locator("#comentario_conteudo").wait_for(
            state="attached",
            timeout=60000
        )

        self.page.evaluate(
            """
            (text) => {
                const textarea = document.querySelector('#comentario_conteudo');
                if (textarea && window.$) {
                    $(textarea).summernote('code', `<p>${text}</p>`);
                }
            }
            """,
            "Estive aqui :)"
        )

        add_btn = self.page.locator("button#comentario-btn").first
        add_btn.wait_for(state="visible", timeout=60000)
        add_btn.click()

        self.page.wait_for_timeout(800)

        # 9. Salva tarefa e aguarda fechamento do modal
        save_btn = modal.locator(
            'button.btn.btn-success:has-text("Salvar"), button[type="submit"].btn.btn-success'
        ).first

        save_btn.wait_for(state="visible", timeout=60000)
        save_btn.click()

        modal.wait_for(state="hidden", timeout=60000)

        return title

    # -----------------------------
    # Busca e abertura de tarefa
    # -----------------------------
    def search_task(self, title: str):
        # Realiza busca pela tarefa
        search_input = self.page.locator("input#busca")
        search_input.wait_for(state="visible", timeout=60000)

        search_input.click()
        search_input.fill("")
        search_input.fill(title)

        search_button = self.page.locator("button.btn.btn-primary.btn-outside-filter[type='submit']")
        search_button.wait_for(state="visible", timeout=60000)
        search_button.click()

        self.page.wait_for_load_state("domcontentloaded")

        # Aguarda resultado aparecer
        task_link = self.page.locator("a[id^='nome_tarefa_']", has_text=title).first
        task_link.wait_for(state="visible", timeout=60000)

    def open_first_result_by_title(self, title: str):
        # Abre a tarefa encontrada
        task_link = self.page.locator("a[id^='nome_tarefa_']", has_text=title).first
        task_link.wait_for(state="visible", timeout=60000)
        task_link.scroll_into_view_if_needed()

        try:
            task_link.click(timeout=10000)
        except Exception:
            task_link.click(force=True)

        # Aguarda abertura do modal de edição
        modal = self.page.locator("#alterTarefa")
        modal.wait_for(state="visible", timeout=60000)

    # -----------------------------
    # Comentários e conclusão
    # -----------------------------
    def add_comment_in_open_task(self, comment: str):
        modal = self.page.locator("#alterTarefa")
        modal.wait_for(state="visible", timeout=60000)

        # Acessa aba de comentários
        comments_tab = modal.locator("a#editar_comentarios-tab")
        comments_tab.wait_for(state="visible", timeout=60000)
        comments_tab.click()

        # Aguarda campo do Summernote
        comment_field = modal.locator("#comentario_editar_conteudo")
        comment_field.wait_for(state="attached", timeout=60000)

        # Insere conteúdo via JS
        self.page.evaluate(
            """
            (text) => {
                const textarea = document.querySelector('#comentario_editar_conteudo');
                if (textarea && window.$) {
                    $(textarea).summernote('code', `<p>${text}</p>`);
                    $(textarea).trigger('change');
                }
            }
            """,
            comment
        )

        # Adiciona comentário
        add_btn = modal.locator("button#comentario_editar-btn").first
        add_btn.wait_for(state="visible", timeout=60000)
        add_btn.click()

        self.page.wait_for_timeout(1000)

    def conclude_task(self):
        # Finaliza a tarefa com confirmação
        modal = self.page.locator("#alterTarefa")
        modal.wait_for(state="visible", timeout=60000)

        conclude_button = modal.locator("#concluirTarefa")
        conclude_button.wait_for(state="visible", timeout=60000)
        conclude_button.click(force=True)

        swal_popup = self.page.locator(".swal2-popup")
        swal_popup.wait_for(state="visible", timeout=60000)

        confirm_button = swal_popup.locator("button.swal2-confirm", has_text="Sim")
        confirm_button.wait_for(state="visible", timeout=60000)
        confirm_button.click(force=True)

        swal_popup.wait_for(state="hidden", timeout=60000)
        modal.wait_for(state="hidden", timeout=60000)

    # -----------------------------
    # Code Review
    # -----------------------------
    def open_code_review_section(self):
        # Expande seção de Code Review
        header = self.page.locator("a.card-header[href='#tarefas_code_review']")
        header.wait_for(state="visible", timeout=60000)

        expanded = header.get_attribute("aria-expanded")

        if expanded != "true":
            header.click()

        self.page.locator("#tarefas_code_review").wait_for(state="visible", timeout=60000)

    def open_task_in_code_review(self, title: str):
        # Abre tarefa dentro da seção de Code Review
        container = self.page.locator("#tarefas_code_review")
        container.wait_for(state="visible", timeout=60000)

        task_link = container.locator("a[data-toggle='modal']", has_text=title).first
        task_link.wait_for(state="visible", timeout=60000)

        task_link.scroll_into_view_if_needed()
        task_link.click(force=True)

        self.page.locator("#alterTarefa").wait_for(state="visible", timeout=60000)

    # -----------------------------
    # Logout
    # -----------------------------
    def logout(self):
        # Localiza menu do usuário que contém a opção de logout
        user_menu = self.page.locator(
            "li.nav-item.dropdown.divider-menu-item"
        ).filter(
            has=self.page.locator("a.dropdown-item[href='/logout']")
        ).first

        user_dropdown = user_menu.locator("a.nav-link.dropdown-toggle")
        user_dropdown.wait_for(state="visible", timeout=60000)

        # Abre dropdown caso ainda não esteja aberto
        if user_dropdown.get_attribute("aria-expanded") != "true":
            user_dropdown.click(force=True)
            self.page.wait_for_timeout(1000)

        # Clica em sair
        logout_link = user_menu.locator("a.dropdown-item[href='/logout']")
        logout_link.wait_for(state="visible", timeout=60000)
        logout_link.click(force=True)

        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    # -----------------------------
    # Fluxo principal
    # -----------------------------
    def run_flow(self):
        self.go_to_tasks()

        title = self.create_task()

        # Etapa 1 - Estimativa
        self.search_task(title)
        self.open_first_result_by_title(title)
        self.add_comment_in_open_task("Etapa de estimativa OK")
        self.conclude_task()

        # Etapa 2 - Desenvolvimento
        self.search_task(title)
        self.open_first_result_by_title(title)
        self.add_comment_in_open_task("Etapa de Desenvolvimento OK")
        self.conclude_task()

        # Etapa 3 - Code Review
        self.open_code_review_section()
        self.open_task_in_code_review(title)
        self.add_comment_in_open_task("Finalizando desenvolvimento")
        self.conclude_task()

        # Logout
        self.logout()
        self.page.wait_for_timeout(500)

    def close(self):
        # Encerra navegador e Playwright
        self.browser.close()
        self.playwright.stop()