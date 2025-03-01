import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QTabWidget,
    QStatusBar, QHBoxLayout, QPushButton, QToolBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class TrackerInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepta las solicitudes de red y bloquea los rastreadores."""
    
    def interceptRequest(self, info):
        blocked_domains = ["example.com", "ads.example.com"]
        host = info.requestUrl().host()
        if any(domain in host for domain in blocked_domains):
            info.block(True)  # Bloquea la solicitud


class SecureBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navegador Seguro")
        self.bookmarks = []

        # Contenedor de pestañas
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Barra de herramientas y navegación
        self.toolbar = self.addToolBar("Navegador Seguro")
        self.create_navigation_buttons()
        self.add_new_tab_button()

        # Barra de marcadores (global)
        self.bookmark_bar = QHBoxLayout()
        self.bookmark_bar_widget = QWidget()
        self.bookmark_bar_widget.setLayout(self.bookmark_bar)
        self.toolbar.addWidget(self.bookmark_bar_widget)

        # Agregar una pestaña inicial
        self.add_new_tab()

        # Configurar seguridad en el navegador activo
        self.setup_tracker_blocking()
        self.setup_private_mode()
        self.setup_security_settings()

        # Agregar botones de marcadores a la interfaz
        self.add_bookmark_buttons()

        # Aplicar estilo QSS
        self.apply_qss()

    def setup_tracker_blocking(self):
        """Configura el bloqueo de rastreadores usando el interceptor."""
        interceptor = TrackerInterceptor()
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.page().profile().setUrlRequestInterceptor(interceptor)

    def setup_private_mode(self):
        """Deshabilita caché y cookies persistentes para modo privado."""
        current_browser = self.get_current_browser()
        if current_browser:
            profile = current_browser.page().profile()
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

    def setup_security_settings(self):
        """Desactiva JavaScript y plugins para mayor seguridad."""
        current_browser = self.get_current_browser()
        if current_browser:
            settings = current_browser.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)

    def add_new_tab(self):
        """Agrega una nueva pestaña con una URL inicial."""
        new_tab = QWidget()
        tab_layout = QVBoxLayout(new_tab)

        # Barra de URL
        url_bar = QLineEdit()
        url_bar.returnPressed.connect(lambda: self.navigate_to_url(url_bar.text()))
        tab_layout.addWidget(url_bar)

        # WebEngineView para mostrar el contenido web
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://duckduckgo.com"))
        tab_layout.addWidget(browser)

        # Botón para cerrar la pestaña (opcional, ya que se puede configurar el QTabWidget como cerrable)
        close_button = QPushButton("X")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(lambda: self.close_current_tab())
        tab_layout.addWidget(close_button)

        # Botón para agregar marcador
        bookmark_button = QPushButton("Agregar Marcador")
        bookmark_button.clicked.connect(lambda: self.add_bookmark(url_bar.text()))
        tab_layout.addWidget(bookmark_button)

        self.tab_widget.addTab(new_tab, "Nueva Pestaña")
        self.tab_widget.setCurrentWidget(new_tab)

    def add_new_tab_button(self):
        """Agrega un botón '+' en la barra de herramientas para abrir una nueva pestaña."""
        new_tab_button = QPushButton("+")
        new_tab_button.setIcon(QIcon.fromTheme("document-new"))
        new_tab_button.clicked.connect(self.add_new_tab)
        self.toolbar.addWidget(new_tab_button)

    def navigate_to_url(self, url):
        """Navega a la URL indicada en la pestaña actual."""
        if not url.startswith("http"):
            url = "http://" + url
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    def go_back(self):
        """Navega hacia atrás en la pestaña actual."""
        current_browser = self.get_current_browser()
        if current_browser and current_browser.history().canGoBack():
            current_browser.back()

    def go_forward(self):
        """Navega hacia adelante en la pestaña actual."""
        current_browser = self.get_current_browser()
        if current_browser and current_browser.history().canGoForward():
            current_browser.forward()

    def go_home(self):
        """Carga la página de inicio en la pestaña actual."""
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl("https://duckduckgo.com"))

    def close_current_tab(self):
        """Cierra la pestaña actual."""
        current_tab_index = self.tab_widget.currentIndex()
        self.tab_widget.removeTab(current_tab_index)

    def get_current_browser(self):
        """Obtiene el QWebEngineView de la pestaña activa buscando entre sus hijos."""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            browsers = current_tab.findChildren(QWebEngineView)
            if browsers:
                return browsers[0]
        return None

    def add_bookmark(self, url):
        """Agrega la URL a la lista de marcadores si no existe ya."""
        if url not in self.bookmarks:
            self.bookmarks.append(url)
            self.update_bookmarks_menu()
            self.status_bar.showMessage(f"Marcador agregado: {url}", 3000)
        else:
            self.status_bar.showMessage(f"El marcador {url} ya existe.", 3000)

    def update_bookmarks_menu(self):
        """Actualiza la barra de marcadores eliminando los botones antiguos y creando nuevos."""
        # Limpiar la barra de marcadores
        for i in reversed(range(self.bookmark_bar.count())):
            widget = self.bookmark_bar.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Crear botón para cada marcador
        for bookmark in self.bookmarks:
            button = QPushButton(bookmark)
            button.clicked.connect(lambda checked, url=bookmark: self.navigate_to_url(url))
            self.bookmark_bar.addWidget(button)

    def add_bookmark_buttons(self):
        """Agrega los botones de marcadores a la barra de herramientas."""
        self.bookmark_bar_widget.setLayout(self.bookmark_bar)
        self.toolbar.addWidget(self.bookmark_bar_widget)

    def create_navigation_buttons(self):
        """Crea los botones de navegación en la barra de herramientas."""
        back_button = QPushButton("Atrás")
        back_button.clicked.connect(self.go_back)
        self.toolbar.addWidget(back_button)

        forward_button = QPushButton("Adelante")
        forward_button.clicked.connect(self.go_forward)
        self.toolbar.addWidget(forward_button)

        home_button = QPushButton("Inicio")
        home_button.clicked.connect(self.go_home)
        self.toolbar.addWidget(home_button)

        bookmark_button = QPushButton("Marcadores")
        bookmark_button.clicked.connect(self.update_bookmarks_menu)
        self.toolbar.addWidget(bookmark_button)

    def apply_qss(self):
        """Aplica un estilo QSS similar a Bootstrap para mejorar el diseño."""
        qss = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        QToolBar {
            background-color: #007bff;
            color: white;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QWidget {
            font-family: Arial, sans-serif;
            font-size: 14px;
        }
        """
        self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Navegador Seguro")
    window = SecureBrowser()
    window.show()
    sys.exit(app.exec_())