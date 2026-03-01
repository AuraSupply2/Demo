import { Link } from "react-router-dom"
export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen flex bg-gray-100">
      
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-6">
        <h2 className="text-xl font-bold mb-6 text-blue-600">
          Sistema Demo
        </h2>

        <nav className="space-y-3">
          <Link to="/" className="block text-gray-700 hover:text-blue-600">
            Dashboard
          </Link>
          <Link to="/clientes" className="block text-gray-700 hover:text-blue-600">
            Clientes
          </Link>
          <Link to="/productos" className="block text-gray-700 hover:text-blue-600">
            Productos
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        
        {/* Header */}
        <header className="bg-white shadow px-6 py-4">
          <h1 className="text-2xl font-semibold text-gray-800">
            Panel de Gestión
          </h1>
        </header>

        {/* Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
}