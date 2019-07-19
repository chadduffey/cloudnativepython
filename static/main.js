import Tweet from "./components/Tweet";

class Main extends React.Component{
	render(){
		return (
 			<div>
 				<h1>Welcome to cloud-native-app!</h1>
 			</div>
 		);
 	}
 }

 let documentReady =() => {
 	ReactDOM.render(
 		<Main/>,
 		document.getElementById('react')
 	);
 };
 
 $(documentReady);