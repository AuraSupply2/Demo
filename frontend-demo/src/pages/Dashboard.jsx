export default function Dashboard() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">
        Bienvenido al Sistema
      </h2>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Clientes</p>
          <h3 className="text-2xl font-bold">0</h3>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Productos</p>
          <h3 className="text-2xl font-bold">0</h3>
        </div>

        <div className="bg-white p-6 rounded-xl shadow">
          <p className="text-gray-500">Ventas</p>
          <h3 className="text-2xl font-bold">$0</h3>
        </div>
      </div>
    </div>
  );
}