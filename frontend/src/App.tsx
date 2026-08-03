import { Admin, Resource } from "react-admin";
import { dataProvider } from "./dataProvider";
import { LinkCreate, LinkEdit, LinkList } from "./links";

export const App = () => (
  <Admin dataProvider={dataProvider} title="URL Shortener Admin">
    <Resource
      name="links"
      list={LinkList}
      create={LinkCreate}
      edit={LinkEdit}
      recordRepresentation="short_name"
    />
  </Admin>
);
