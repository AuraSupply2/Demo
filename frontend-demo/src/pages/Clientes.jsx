import { useEffect, useState } from "react";
import { getClientes } from "../api";

export default function Clientes() {
  const [clientes, setClientes] = useState([]);

  useEffect(() => {
    async function cargarClientes() {
      const data = await getClientes();
      setClientes(data);
    }

    cargarClientes();
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">Gestión de Clientes</h2>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="p-4">Nombre</th>
              <th className="p-4">Email</th>
              <th className="p-4">Teléfono</th>
            </tr>
          </thead>
          <tbody>
            {clientes.map((cliente) => (
              <tr key={cliente.id} className="border-t">
                <td className="p-4">{cliente.nombre}</td>
                <td className="p-4">{cliente.email}</td>
                <td className="p-4">{cliente.telefono}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}