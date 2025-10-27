import { useEffect, useState } from "react";
import { Context } from "@/context/GlobalContext";
import { useContext } from "react";
import { httpClient } from "@/httpClient";

export function Dashboard() {
  const { setHeaderTitle } = useContext(Context);
  const [sData, setSData] = useState<any>(null);
  useEffect(() => {
    setHeaderTitle?.("Admin Dashboard");
  }, [setHeaderTitle]);

  useEffect(() => {
    httpClient.getRuns().then((data) => {
      setSData(data);
    });
  }, []);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="table">
          {/* head */}
          <thead>
            <tr>
              <th></th>
              <th>Job Id</th>
              <th>Sender</th>
              <th>Status</th>
              <th>Created At</th>
              <th>File Name</th>
            </tr>
          </thead>
          <tbody>
            {sData?.map((run: any, index: number) => (
              <tr key={run.job_id}>
                <th>{index + 1}</th>
                <td>{run.job_id}</td>
                <td>{run.sender_id}</td>
                <td>{run.status}</td>
                <td>{new Date(run.started_at).toLocaleString()}</td>
                <td>{run.doc_filename}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
